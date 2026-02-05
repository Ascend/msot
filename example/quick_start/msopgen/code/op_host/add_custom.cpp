/**
 * @file add_custom.cpp
 *
 * Copyright (C) 2023-2024. Huawei Technologies Co., Ltd. All rights reserved.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 */
#include "add_custom_tiling.h"
#include "register/op_def_registry.h"

namespace optiling {
    /**
     * 此函数使用CANN框架编程模式，没学过可能看不懂，当前只需理解设置了3个数字信息(数据总长/tile数/核数)可传递到核函数即可，
     * 不影响对算子工具使用的理解，详细原理流程请参考《Ascend C算子开发指南》相关章节。
     * 
     * 功能：执行算子分块计算相关信息计算(数据总长度，tile数量等)，注册到下面算子定义中后，CANN框架会调用并根据返回的数据进行后续计算。
     * 
     * 参数TilingContext* context：输入和输出都通过此上下文结构参数来承载，
     * 开发者可以从上下文结构中获取算子的输入、输出以及属性信息，也就是Tiling实现的输入，经过Tiling计算后，
     * 获取到TilingData数据结构（带有切分算法相关参数）、blockDim变量等，也就是Tiling实现的输出，
     * 并将这些输出设置到上下文结构中，供后续计算时使用。
     * 
     */
    static ge::graphStatus TilingFunc(gert::TilingContext *context)
    {
        // 第一步：设置tiling信息(数据总长/tile数量)到context上下文中
        uint32_t totalLength = context->GetInputShape(0)->GetOriginShape().GetShapeSize(); // 获取输入数据的总长度
        const uint32_t TILE_NUM = 8;  // 每个核上分8个tile进行计算
        TilingData tiling;
        tiling.set_totalLength(totalLength);
        tiling.set_tileNum(TILE_NUM);
        tiling.SaveToBuffer(context->GetRawTilingData()->GetData(), context->GetRawTilingData()->GetCapacity());
        context->GetRawTilingData()->SetDataSize(tiling.GetDataSize()); // 将tileing数据结构保存到上下文结构中

        // 第二步：设置使用多少个AICore核进行计算的信息到context上下文中
        const uint32_t BLOCK_DIM = 8; // 使用8个核进行计算
        context->SetBlockDim(BLOCK_DIM);
        
        return ge::GRAPH_SUCCESS;
    }
} // namespace optiling

namespace ops {
    /**
     * 使用CANN框架编程模式，没学过可能看不懂，当前只需理解设置了2个入参1个出参的算子函数信息即可，不影响对算子工具使用的理解，
     * 详细原理流程请参考《Ascend C算子开发指南》相关章节。
     * 
     * 功能：该类定义了一个自定义的加法算子，支持两个FLOAT16类型张量的加法运算，
     * 并配置了在不同Ascend芯片上的运行参数。
     */
    class AddCustom : public OpDef {
    public:
        explicit AddCustom(const char *name) : OpDef(name)
        {
            // 配置第一个输入参数x：必需参数，数据类型为FLOAT16，格式为ND
            this->Input("x")
                .ParamType(REQUIRED)
                .DataType({ge::DT_FLOAT16})
                .Format({ge::FORMAT_ND});
            
            // 配置第二个输入参数y：必需参数，数据类型为FLOAT16，格式为ND
            this->Input("y")
                .ParamType(REQUIRED)
                .DataType({ge::DT_FLOAT16})
                .Format({ge::FORMAT_ND});
            
            // 配置输出参数z：必需参数，数据类型为FLOAT16，格式为ND
            this->Output("z")
                .ParamType(REQUIRED)
                .DataType({ge::DT_FLOAT16})
                .Format({ge::FORMAT_ND});

            // 配置AICore计算单元，设置分块策略和兼容的芯片型号
            this->AICore()
                .SetTiling(optiling::TilingFunc) // 引用上面定义的tiling函数
                .AddConfig("ascend910b")
                .AddConfig("ascend910")
                .AddConfig("ascend310p")
                .AddConfig("ascend310b");
        }
    };

    // 注册AddCustom算子到算子库中
    OP_ADD(AddCustom);
} // namespace ops
