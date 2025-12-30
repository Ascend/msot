/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2025-2025. All rights reserved.
 */
#ifndef DATA_UTILS_H
#define DATA_UTILS_H
#include <iostream>

namespace OperatorSample {

#define CHECK_ACL(x)                                 \
    do {                                             \
        assert((x == ACL_RT_SUCCESS) && "error.\n"); \
    } while (0)

} // namespace OperatorSample

#endif // DATA_UTILS_H
