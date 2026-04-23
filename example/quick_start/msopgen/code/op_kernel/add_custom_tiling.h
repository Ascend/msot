/**
 * @file add_custom_tiling.h
 *
 * Copyright (C) 2023-2024. Huawei Technologies Co., Ltd. All rights reserved.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 */
#ifndef ADD_CUSTOM_TILING_H
#define ADD_CUSTOM_TILING_H
#include "register/tilingdata_base.h"

namespace optiling {

    // Tiling算法信息结构体定义，比如数据总长度/TileNum等，由开发者自行设计，由框架负责传递
    BEGIN_TILING_DATA_DEF(TilingData) // 声明Tiling结构体名称
        TILING_DATA_FIELD_DEF(uint32_t, totalLength);  // 自定义结构体成员的类型和名称：总计算数据量
        TILING_DATA_FIELD_DEF(uint32_t, tileNum);      // 自定义结构体成员的类型和名称：每个核上总计算数据分块个数
    END_TILING_DATA_DEF;

    // 将TilingData类注册到对应的AddCustom算子
    REGISTER_TILING_DATA_CLASS(AddCustom, TilingData)

  } // namespace optiling

#endif // ADD_CUSTOM_TILING_H
