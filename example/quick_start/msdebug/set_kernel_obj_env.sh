#!/bin/bash
# =============================================================================
# set_kernel_obj_env.sh - 算子调试内核目标文件环境变量配置脚本
#
# 功能描述:
#   本脚本用于自动查找算子编译生成的内核目标文件 (.o)，并设置 LAUNCH_KERNEL_PATH
#   环境变量，供 msdebug 算子调试工具使用。
#
# 主要功能:
#   1. 在指定路径下递归搜索匹配前缀的 .o 目标文件
#   2. 自动选择最新修改的目标文件
#   3. 设置 LAUNCH_KERNEL_PATH 环境变量指向该文件
#
# 使用方法:
#   source set_kernel_obj_env.sh [search_path] [prefix]
#
# 参数说明:
#   search_path - 搜索路径 (可选)
#                 默认: $ASCEND_OPP_PATH (若已设置)，否则为 /usr/local/Ascend
#   prefix      - 目标文件前缀 (可选)
#                 默认: AddCustom (将匹配 AddCustom_*.o)
#
# 注意事项:
#   - 必须使用 source 命令调用，不能直接执行
#   - 需要确保搜索路径下存在对应的 .o 文件
#
# 示例:
#   source set_kernel_obj_env.sh                          # 使用默认路径和前缀
#   source set_kernel_obj_env.sh /path/to/opp             # 指定搜索路径
#   source set_kernel_obj_env.sh /path/to/opp MyOperator  # 指定路径和前缀
# =============================================================================

# 检查是否被 source 调用
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: This script must be sourced, not executed directly." >&2
    echo "Usage: source $0 [search_path] [prefix]" >&2
    echo "  - search_path: directory to search" >&2
    echo "                 (default: \$ASCEND_OPP_PATH if set, else /usr/local/Ascend)" >&2
    echo "  - prefix:     object file prefix (default: AddCustom)" >&2
    exit 1
fi

# 参数处理：
# - $1: 搜索路径（若提供且非空，则使用）
# - 否则：使用 ASCEND_OPP_PATH 环境变量（若已设置）
# - 否则：默认为 /usr/local/Ascend
if [ -n "$1" ]; then
    SEARCH_PATH="$1"
elif [ -n "$ASCEND_OPP_PATH" ]; then
    SEARCH_PATH="$ASCEND_OPP_PATH"
else
    SEARCH_PATH="/usr/local/Ascend"
fi

SEARCH_PATH="${SEARCH_PATH%/ascend-toolkit*}"

# 第二个参数：文件前缀，默认 AddCustom
PREFIX="${2:-AddCustom}"

# 构造匹配模式
PATTERN="${PREFIX}_*.o"

# 查找最新 .o 文件
FILES=$(find "$SEARCH_PATH" -type f -name "$PATTERN" 2>/dev/null)
if [ -n "$FILES" ]; then
    O_FILE=$(printf '%s\n' "$FILES" | xargs ls -t 2>/dev/null | head -n 1)
else
    O_FILE=""
fi

if [ -n "$O_FILE" ]; then
    export LAUNCH_KERNEL_PATH="$O_FILE"
    echo "Find obj file, exec cmd:export LAUNCH_KERNEL_PATH=$LAUNCH_KERNEL_PATH"
else
    echo "Error: No ${PATTERN} file found under '${SEARCH_PATH}'" >&2
    return 1
fi