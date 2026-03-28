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
#
# Build and run the custom operator example.
# Usage: bash run.sh [npu_id]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

# --------------- Resolve Ascend toolkit install path ---------------

resolve_install_path() {
    if [[ -n "${ASCEND_INSTALL_PATH:-}" ]]; then
        echo "${ASCEND_INSTALL_PATH}"
    elif [[ -n "${ASCEND_HOME_PATH:-}" ]]; then
        echo "${ASCEND_HOME_PATH}"
    elif [[ -d "${HOME}/Ascend/ascend-toolkit/latest" ]]; then
        echo "${HOME}/Ascend/ascend-toolkit/latest"
    else
        echo "/usr/local/Ascend/ascend-toolkit/latest"
    fi
}

REAL_ASCEND_INSTALL_PATH="$(resolve_install_path)"
readonly REAL_ASCEND_INSTALL_PATH
export REAL_ASCEND_INSTALL_PATH

# --------------- Validate and source environment --------------------

SETENV_SCRIPT="${REAL_ASCEND_INSTALL_PATH}/bin/setenv.bash"
if [[ ! -f "${SETENV_SCRIPT}" ]]; then
    echo "ERROR: setenv.bash not found at ${SETENV_SCRIPT}" >&2
    echo "       Please verify the Ascend toolkit installation." >&2
    exit 1
fi
# shellcheck source=/dev/null
source "${SETENV_SCRIPT}"

export DDK_PATH="${REAL_ASCEND_INSTALL_PATH}"
ARCH="$(arch)"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
export NPU_HOST_LIB="${REAL_ASCEND_INSTALL_PATH}/${ARCH}-${OS}/devlib"

# --------------- Run ------------------------------------------------

python3 "${SCRIPT_DIR}/exec.py" "$@"
