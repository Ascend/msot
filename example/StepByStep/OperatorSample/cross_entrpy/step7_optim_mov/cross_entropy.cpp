/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2025-2025. All rights reserved.
 * Function : loss = F.cross_entropy(logits, labels)
 */
#include "kernel_operator.h"
#include "utils/config.h"
#include "utils/kernel_utils.h"

using namespace AscendC;
using namespace OperatorSample;

class CrossEntropy {
public:
    __aicore__ inline CrossEntropy() {}
    __aicore__ inline void Init(GM_ADDR logit, GM_ADDR label, GM_ADDR output, GM_ADDR workspace,
        GM_ADDR syncCore, GM_ADDR tilingData)
    {
        InitVar(tilingData);
        logitGm_.SetGlobalBuffer(reinterpret_cast<__gm__ float*>(logit) + logitOffset_, tileNum_ * numClass_);
        labelGm_.SetGlobalBuffer(reinterpret_cast<__gm__ int64_t*>(label) + tileOffset_, tileNum_);
        lossGm_.SetGlobalBuffer(reinterpret_cast<__gm__ float*>(output), 1);
        lossBufferGm_.SetGlobalBuffer(reinterpret_cast<__gm__ float*>(workspace) +
            workSpaceOffset_ / sizeof(float), workSpaceSize_);
        syncGm_.SetGlobalBuffer(reinterpret_cast<__gm__ int32_t*>(syncCore), blockDim_ * 8);
        pipe_.InitBuffer(inQueLogit_, 1, numClass_ * sizeof(float));
        pipe_.InitBuffer(workQueSync_, 1, blockDim_ * 32);
        InitOpBuffer();
    }

    __aicore__ inline void Process()
    {
        for (int32_t i = 0; i < tileNum_; ++i) {
            CopyIn(i);
            ComputeTileLoss(i);
        }
        SyncAllBlock();
        CalcMeanLoss();
    }

private:
    __aicore__ inline void InitVar(GM_ADDR tilingData)
    {
        blockIdx_ = GetBlockIdx();
        auto tiling = reinterpret_cast<__gm__ uint64_t*>(tilingData);
        batchSize_ = tiling[0];
        numClass_ = tiling[1];
        blockDim_ = tiling[2];
        tailSize_ =  batchSize_ % blockDim_;
        tileNum_ = batchSize_ / blockDim_;
        if (blockIdx_ < tailSize_) {
            tileNum_++;
            tileOffset_ += blockIdx_ * tileNum_;
            workSpaceOffset_ += Align<GM_CACHE_SIZE_ALIGN_SIZE>(tileNum_ * sizeof(float)) * blockIdx_;
        } else {
            tileOffset_ += tailSize_ * (tileNum_ + 1);
            workSpaceOffset_ += Align<GM_CACHE_SIZE_ALIGN_SIZE>((tileNum_ + 1) * sizeof(float)) * tailSize_;
            tileOffset_ += (blockIdx_ - tailSize_) * tileNum_;
            workSpaceOffset_ += Align<GM_CACHE_SIZE_ALIGN_SIZE>(tileNum_ * sizeof(float)) * (blockIdx_ - tailSize_);
        }
        logitOffset_ = tileOffset_ * numClass_;
        workSpaceSize_ = Align<GM_CACHE_SIZE_ALIGN_SIZE>(tileNum_ * sizeof(float));
        logitMovNums_ = Align<DATA_COPY_ALIGN_SIZE>(numClass_ * sizeof(float)) / sizeof(float);
    }

    __aicore__ inline void InitOpBuffer()
    {
        uint32_t buffSize = Align<UB_ALIGN_SIZE>(sizeof(float)) + Align<UB_ALIGN_SIZE>(numClass_ * sizeof(float));
        pipe_.InitBuffer(this->calcBuf_, buffSize);
        size_t bufOffset = 0;
        this->reduceSumLocal_ = this->calcBuf_.template Get<float>(1);
        bufOffset += Align<UB_ALIGN_SIZE>(sizeof(float));
        this->labelOneHotLocal_ = this->calcBuf_.template GetWithOffset<float>(numClass_, bufOffset);
    }

    __aicore__ inline void CopyIn(int32_t progress)
    {
        LocalTensor<float> logitLocal = inQueLogit_.AllocTensor<float>();
        DataCopy(logitLocal, logitGm_[progress * numClass_], logitMovNums_);
        inQueLogit_.EnQue(logitLocal);
    }

    __aicore__ inline void ComputeTileLoss(int32_t progress)
    {
        LocalTensor<float> logitLocal = inQueLogit_.DeQue<float>();
        Exp(logitLocal, logitLocal, numClass_);
        PipeBarrier<PIPE_V>();
        ReduceSum<float>(reduceSumLocal_, logitLocal, logitLocal, numClass_);
        TEventID eventIdVToS = GetTPipePtr()->FetchEventID(HardEvent::V_S);
        SetFlag<HardEvent::V_S>(eventIdVToS);
        WaitFlag<HardEvent::V_S>(eventIdVToS);
        float sum = reduceSumLocal_.GetValue(0);
        PipeBarrier<PIPE_V>();
        Muls(logitLocal, logitLocal, 1 / sum, numClass_);
        int64_t labelIdx = labelGm_.GetValue(progress);
        Duplicate(labelOneHotLocal_, float(0.0), numClass_);
        eventIdVToS = GetTPipePtr()->FetchEventID(HardEvent::V_S);
        SetFlag<HardEvent::V_S>(eventIdVToS);
        WaitFlag<HardEvent::V_S>(eventIdVToS);
        labelOneHotLocal_.SetValue(labelIdx, float(1.0));
        PipeBarrier<PIPE_V>();
        TEventID eventIdSToV = GetTPipePtr()->FetchEventID(HardEvent::S_V);
        SetFlag<HardEvent::S_V>(eventIdSToV);
        WaitFlag<HardEvent::S_V>(eventIdSToV);
        Mul(logitLocal, logitLocal, labelOneHotLocal_, numClass_);
        PipeBarrier<PIPE_V>();
        Log(logitLocal, logitLocal, numClass_);
        PipeBarrier<PIPE_V>();
        Muls(logitLocal, logitLocal, float(-1.0), numClass_);
        eventIdVToS = GetTPipePtr()->FetchEventID(HardEvent::V_S);
        SetFlag<HardEvent::V_S>(eventIdVToS);
        WaitFlag<HardEvent::V_S>(eventIdVToS);
        float loss = logitLocal.GetValue(labelIdx);
        lossBufferGm_.SetValue(progress, loss);
        inQueLogit_.FreeTensor(logitLocal);
    }

    __aicore__ inline void SyncAllBlock()
    {
        LocalTensor<int32_t> workLocal = workQueSync_.AllocTensor<int32_t>();
        SyncAll(syncGm_, workLocal);
        workQueSync_.FreeTensor(workLocal);
    }

    __aicore__ inline void CalcMeanLoss()
    {
        if (blockIdx_ == 0) {
            uint32_t copyNums = Align<DATA_COPY_ALIGN_SIZE>(workSpaceSize_ * blockDim_) / sizeof(float);
            LocalTensor<float> logitLocal = inQueLogit_.AllocTensor<float>();
            DataCopy(logitLocal, lossBufferGm_, copyNums);
            TEventID eventIdMte2ToV = GetTPipePtr()->FetchEventID(HardEvent::MTE2_V);
            SetFlag<HardEvent::MTE2_V>(eventIdMte2ToV);
            WaitFlag<HardEvent::MTE2_V>(eventIdMte2ToV);
            ReduceSum<float>(logitLocal, logitLocal, logitLocal, copyNums);
            TEventID eventIdVToS = GetTPipePtr()->FetchEventID(HardEvent::V_S);
            SetFlag<HardEvent::V_S>(eventIdVToS);
            WaitFlag<HardEvent::V_S>(eventIdVToS);
            lossGm_.SetValue(0, logitLocal(0) / batchSize_);
            inQueLogit_.FreeTensor(logitLocal);
        }
    }

private:
    TPipe pipe_;
    TQue<QuePosition::VECIN, 1> inQueLogit_;
    TQue<AscendC::QuePosition::VECIN, 1> workQueSync_;
    TBuf<TPosition::VECCALC> calcBuf_;

    GlobalTensor<float> logitGm_;
    GlobalTensor<int64_t> labelGm_;
    GlobalTensor<float> lossGm_;
    GlobalTensor<float> lossBufferGm_;
    GlobalTensor<int32_t> syncGm_;
    LocalTensor<float> reduceSumLocal_;
    LocalTensor<float> labelOneHotLocal_;

    uint64_t batchSize_{};
    uint64_t numClass_{};
    uint64_t blockDim_{};
    uint64_t tailSize_{};
    uint64_t logitOffset_{};
    uint64_t tileNum_{};
    uint64_t workSpaceSize_{};
    uint64_t blockIdx_{};
    uint64_t tileOffset_{};
    uint64_t workSpaceOffset_{};
    uint64_t logitMovNums_{};
};

extern "C" __global__ __aicore__ void cross_entropy(GM_ADDR logit, GM_ADDR label, GM_ADDR output, GM_ADDR workspace,
    GM_ADDR syncGm, GM_ADDR tilingData)
{
    KERNEL_TASK_TYPE_DEFAULT(KERNEL_TYPE_AIV_ONLY);
    CrossEntropy op;
    op.Init(logit, label, output, workspace, syncGm, tilingData);
    op.Process();
}

