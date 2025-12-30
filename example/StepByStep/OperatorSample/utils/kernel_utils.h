/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2025-2025. All rights reserved.
 */
#ifndef KERNEL_UTILS_H
#define KERNEL_UTILS_H

namespace OperatorSample {

template <uint32_t AlignSize>
__aicore__ inline uint32_t Align(uint32_t size)
{
    static_assert(AlignSize != 0, "align must not be zero");
    return ((size + AlignSize - 1) / AlignSize) * AlignSize;
}

} // namespace OperatorSample

#endif // KERNEL_UTILS_H
