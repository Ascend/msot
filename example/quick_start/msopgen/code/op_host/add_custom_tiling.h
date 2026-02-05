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

    // Tile算法信息结构体定义，比如数据总长/TileNum等，由开发者自行设计，框架进行传递
    BEGIN_TILING_DATA_DEF(TilingData) // 声明tiling结构名字
        TILING_DATA_FIELD_DEF(uint32_t, totalLength);  // 自行定义的结构成员的类型和名字：总计算数据量
        TILING_DATA_FIELD_DEF(uint32_t, tileNum);      // 自行定义的结构成员的类型和名字：每个核上总计算数据分块个数
    END_TILING_DATA_DEF;

    // 注册算子tilingdata类到对应的AddCustom算子
    REGISTER_TILING_DATA_CLASS(AddCustom, TilingData)

  } // namespace optiling

#endif // ADD_CUSTOM_TILING_H
