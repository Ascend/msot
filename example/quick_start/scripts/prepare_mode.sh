#!/bin/bash
# Copyright (c) 2026 Huawei Technologies Co., Ltd.
# Licensed under Mulan PSL v2. See the repository LICENSE.
set -euo pipefail
script_path=${BASH_SOURCE[0]}
script_dir=${script_path%/*}
[[ "$script_dir" != "$script_path" ]] || script_dir=.
script_dir=$(cd -- "$script_dir" && pwd -P)
if ! command -v python3 >/dev/null 2>&1; then
    echo "[FAIL] Python 3 is required; prepare the documented CANN environment first." >&2
    exit 1
fi
exec python3 -B "$script_dir/_helpers.py" prepare-mode "$@"
