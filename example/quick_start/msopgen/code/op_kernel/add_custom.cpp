/**
 * @file add_custom.cpp
 *
 * Copyright (C) 2022-2024. Huawei Technologies Co., Ltd. All rights reserved.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 */
#include "kernel_operator.h"
constexpr int32_t BUFFER_NUM = 2; // tensor num for each queue

class KernelAdd {
public:
    __aicore__ inline KernelAdd() {}
    /**
     * @brief 初始化函数，用于设置数据块长度、分片数量以及全局内存和流水线缓冲区
     *
     * @param x 全局内存中输入数据X的起始地址
     * @param y 全局内存中输入数据Y的起始地址
     * @param z 全局内存中输出数据Z的起始地址
     * @param totalLength 数据总长度
     * @param tileNum 分片数量
     */
    __aicore__ inline void Init(GM_ADDR x, GM_ADDR y, GM_ADDR z, uint32_t totalLength, uint32_t tileNum)
    {
        // 计算当前AI Core处理的数据长度，将总长度按AI Core数量均分
        this->blockLength = totalLength / AscendC::GetBlockNum();
        this->tileNum = tileNum ? tileNum : 1;
        // 计算每个Tiling分片的长度，考虑BUFFER_NUM个流水线缓冲区的划分
        this->tileLength = this->blockLength / this->tileNum / BUFFER_NUM;

        // 设置全局内存缓冲区，为当前AI Core分配其负责的全局共享内存区域
        xGm.SetGlobalBuffer((__gm__ DTYPE_X *)x + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
        yGm.SetGlobalBuffer((__gm__ DTYPE_Y *)y + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
        zGm.SetGlobalBuffer((__gm__ DTYPE_Z *)z + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);

        // 初始化流水线缓冲区，分别为输入队列X、Y和输出队列Z在UB(Local Memory)中分配内存空间
        pipe.InitBuffer(inQueueX, BUFFER_NUM, this->tileLength * sizeof(DTYPE_X));
        pipe.InitBuffer(inQueueY, BUFFER_NUM, this->tileLength * sizeof(DTYPE_Y));
        pipe.InitBuffer(outQueueZ, BUFFER_NUM, this->tileLength * sizeof(DTYPE_Z));
    }
        /**
         * @brief 处理数据的核心函数，执行数据搬运、AI Core计算和结果回写的流水线循环
         *
         * 该函数通过循环处理多个Tiling分片，每个循环包含三个阶段：
         * 1. 调用CopyIn函数将数据从全局共享内存(Gobal Memory)搬运至UB(Local Memory)
         * 2. 调用Compute函数在AI Core上执行向量化加法计算
         * 3. 调用CopyOut函数将结果从UB(Local Memory)回写至全局共享内存(Gobal Memory)
         *
         * 循环次数由tileNum和BUFFER_NUM两个成员变量的乘积确定，
         * 表示需要处理的Tiling分片总数。
         */
    __aicore__ inline void Process()
    {
        // 计算总的流水线循环次数
        int32_t loopCount = this->tileNum * BUFFER_NUM;

        // 循环处理每个Tiling分片
        for (int32_t i = 0; i < loopCount; i++) {
            CopyIn(i);
            Compute(i);
            CopyOut(i);
        }
    }

private:
    /**
        * @brief 将全局内存中的数据分片搬运到本地UB缓冲区(Local Memory)
        * @param progress 当前处理的Tiling分片索引，用于计算全局共享内存中的数据偏移量
        *
        * 该函数负责从全局共享内存中读取第progress个Tiling分片，并将其搬运到本地LocalTensor中，
        * 然后将LocalTensor入队到对应的输入队列中，为后续AI Core计算做准备。
        */
    __aicore__ inline void CopyIn(int32_t progress)
    {
        // 分配本地LocalTensor用于存储输入数据
        AscendC::LocalTensor<DTYPE_X> xLocal = inQueueX.AllocTensor<DTYPE_X>();
        AscendC::LocalTensor<DTYPE_Y> yLocal = inQueueY.AllocTensor<DTYPE_Y>();

        // 从全局共享内存(Gobal Memory)搬运数据到本地UB(Local Memory)
        AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], this->tileLength);
        AscendC::DataCopy(yLocal, yGm[progress * this->tileLength], this->tileLength);

        // 将本地LocalTensor入队供后续计算使用
        inQueueX.EnQue(xLocal);
        inQueueY.EnQue(yLocal);
    }
    /**
        * @brief 执行张量加法计算的核心函数
        * @param progress 进度标识，用于控制计算流程
        *
        * 该函数从输入队列中获取两个LocalTensor，执行向量化加法运算后将结果存入输出队列。
        * 主要包括数据出队、UB内存分配、AI Core向量化加法计算、结果入队和UB内存释放等步骤。
        */
    __aicore__ inline void Compute(int32_t progress)
    {
        // 从输入队列中取出第一个操作数LocalTensor
        AscendC::LocalTensor<DTYPE_X> xLocal = inQueueX.DeQue<DTYPE_X>();
        // 从输入队列中取出第二个操作数LocalTensor
        AscendC::LocalTensor<DTYPE_Y> yLocal = inQueueY.DeQue<DTYPE_Y>();
        // 从输出队列中分配结果LocalTensor的UB内存空间
        AscendC::LocalTensor<DTYPE_Z> zLocal = outQueueZ.AllocTensor<DTYPE_Z>();
        // 执行AI Core向量化加法运算：z = x + y
        AscendC::Add(zLocal, xLocal, yLocal, this->tileLength);
        // 将计算结果LocalTensor放入输出队列
        outQueueZ.EnQue<DTYPE_Z>(zLocal);
        // 释放第一个输入LocalTensor的UB内存资源
        inQueueX.FreeTensor(xLocal);
        // 释放第二个输入LocalTensor的UB内存资源
        inQueueY.FreeTensor(yLocal);
    }
    /**
     * @brief 将本地LocalTensor数据回写到全局内存(Gobal Memory)输出区域
     *
     * 该函数从输出队列中获取一个LocalTensor，将其数据复制到全局共享内存的指定位置，
     * 然后释放该LocalTensor的UB资源。主要用于AI Core算子的结果输出操作。
     *
     * @param progress 当前处理进度索引，用于计算全局共享内存中的目标写入位置
     *
     * @return 无返回值
     */
    __aicore__ inline void CopyOut(int32_t progress)
    {
        // 从输出队列中获取LocalTensor
        AscendC::LocalTensor<DTYPE_Z> zLocal = outQueueZ.DeQue<DTYPE_Z>();
        // 将LocalTensor数据从UB(Local Memory)回写到全局共享内存(Gobal Memory)
        AscendC::DataCopy(zGm[progress * this->tileLength], zLocal, this->tileLength);
        // 释放LocalTensor的UB(Local Memory)资源
        outQueueZ.FreeTensor(zLocal);
    }

private:
    AscendC::TPipe pipe;
    AscendC::TQue<AscendC::TPosition::VECIN, BUFFER_NUM> inQueueX, inQueueY;
    AscendC::TQue<AscendC::TPosition::VECOUT, BUFFER_NUM> outQueueZ;
    AscendC::GlobalTensor<DTYPE_X> xGm;
    AscendC::GlobalTensor<DTYPE_Y> yGm;
    AscendC::GlobalTensor<DTYPE_Z> zGm;
    uint32_t blockLength;
    uint32_t tileNum;
    uint32_t tileLength;
};

/**
 * @brief 自定义加法核函数，在AI Core上执行向量加法操作
 *
 * 该函数作为昇腾AI Core算子的入口，负责初始化加法操作并处理Tiling分片计算。
 * 函数通过解析Tiling配置信息来管理大规模数据在多AI Core上的协同处理。
 *
 * @param x 输入向量x的全局内存地址
 * @param y 输入向量y的全局内存地址
 * @param z 输出向量z的全局内存地址
 * @param workspace 工作空间内存地址，用于临时存储（当前未使用）
 * @param tiling Tiling配置信息的内存地址，包含数据分片策略与调度参数
 *
 * @note 该函数无返回值，计算结果直接写入输出地址z
 */
extern "C" __global__ __aicore__ void add_custom(GM_ADDR x, GM_ADDR y, GM_ADDR z, GM_ADDR workspace, GM_ADDR tiling)
{
    // 获取Tiling配置数据
    GET_TILING_DATA(tiling_data, tiling);

    // 创建并初始化加法算子对象
    KernelAdd op;
    op.Init(x, y, z, tiling_data.totalLength, tiling_data.tileNum);

    // 执行加法计算流水线
    op.Process();
}

#ifndef ASCENDC_CPU_DEBUG
// call of kernel function
/**
 * @brief 启动自定义向量加法算子的 AI Core 核函数
 *
 * 该函数封装了昇腾 AI Core 上的核函数调用，用于执行用户自定义的向量加法运算。
 * 通过传入 Tiling 配置、工作空间及设备内存指针，完成算子在 NPU 上的调度与执行。
 *
 * @param core_num 本次启动的AI Core数量（对应原blockDim语义）
 * @param l2ctrl 预留参数
 * @param stream 流对象，用于异步任务提交与执行依赖管理
 * @param x 输入张量 x 的设备内存地址(Gobal Memory)
 * @param y 输入张量 y 的设备内存地址(Gobal Memory)
 * @param z 输出张量 z 的设备内存地址，用于存储 x + y 的结果(Gobal Memory)
 * @param workspace 临时工作空间设备地址，供核函数内部中间计算使用
 * @param tiling Tiling策略数据结构地址，定义数据分块方式以优化 AI Core 计算吞吐与内存带宽利用率
 */
void add_custom_do(uint32_t blockDim, void *l2ctrl, void *stream, uint8_t *x, uint8_t *y, uint8_t *z,
                   uint8_t *workspace, uint8_t *tiling)
{
    // 启动AI Core执行自定义加法运算
    add_custom<<<blockDim, l2ctrl, stream>>>(x, y, z, workspace, tiling);
}
#endif