#!/bin/bash
# -------------------------------------------------------------------------
# This file is part of the MindStudio project.
# Copyright (c) 2025 Huawei Technologies Co.,Ltd.
#
# MindStudio is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#
#          http://license.coscl.org.cn/MulanPSL2
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
# -------------------------------------------------------------------------

# 对 mskpp 模块产出的 wheel 执行 auditwheel repair，
# 为其添加完整 manylinux 兼容标签（manylinux2014 / manylinux_2_17 等），
# 使 wheel 能在更老的 manylinux 系统上安装。
#
# 用法: repair_mskpp_wheel.sh <wheel所在目录>
#
# 若环境中没有 auditwheel，静默跳过。

set -e

WHEEL_DIR="${1:-.}"

# 无 auditwheel 时静默跳过（非 manylinux 构建环境）
if ! command -v auditwheel >/dev/null 2>&1; then
    echo "[repair_mskpp_wheel] auditwheel not found, skip wheel repair."
    exit 0
fi

repaired_count=0
for whl in "${WHEEL_DIR}"/mindstudio_kpp-*.whl; do
    # glob 未匹配到任何文件时跳过
    [ -f "$whl" ] || continue

    # 已包含 manylinux2014 标签的跳过（避免重复修复）
    if echo "$whl" | grep -q 'manylinux2014'; then
        echo "[repair_mskpp_wheel] Already repaired, skip: $(basename "$whl")"
        continue
    fi

    echo "[repair_mskpp_wheel] Repairing: $(basename "$whl")"
    auditwheel repair "$whl" -w "${WHEEL_DIR}"/

    # 修复成功后删除原始 wheel（只保留修复后的版本）
    rm -f "$whl"
    repaired_count=$((repaired_count + 1))
done

if [ $repaired_count -gt 0 ]; then
    echo "[repair_mskpp_wheel] Repaired ${repaired_count} wheel(s)."
else
    echo "[repair_mskpp_wheel] No wheels to repair."
fi
