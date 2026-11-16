#!/bin/bash
# Copyright (c) 2026 Huawei Technologies Co., Ltd.
# Licensed under Mulan PSL v2. See the repository LICENSE.

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    printf '\033[31m%s [ERROR] This script must be sourced; please use: source %s [--session-only].\033[0m\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" "${BASH_SOURCE[0]}" >&2
    exit 1
fi

_msot_set_chip_soc_env() {
    local argument script_path script_dir soc declaration
    for argument in "$@"; do
        case "$argument" in
            --session-only) ;; # Forwarded to the query helper below.
            --help|-h)
                printf '%s\n' \
                    'Usage: source set_chip_soc_env.sh [--session-only] [--help]' \
                    'Query acl.get_soc_name() and export MY_STUDY_VAR_CHIP_SOC_TYPE in the current Shell.' \
                    'By default, create or reuse /etc/profile.d/custom-env.sh for login Shells.' \
                    'Without write permission, warn and continue for the current session only.' \
                    '  --session-only  Do not read or write profile configuration.'
                return 0
                ;;
            *)
                printf '\033[31m%s [ERROR] Unknown argument: %s; please use --help.\033[0m\n' \
                    "$(date '+%Y-%m-%d %H:%M:%S')" "$argument" >&2
                return 2
                ;;
        esac
    done
    if ! command -v python3 >/dev/null 2>&1; then
        printf '\033[31m%s [ERROR] Python 3 is required; please load the documented CANN environment.\033[0m\n' \
            "$(date '+%Y-%m-%d %H:%M:%S')" >&2
        return 1
    fi
    declaration=$(declare -p MY_STUDY_VAR_CHIP_SOC_TYPE 2>/dev/null || true)
    if [[ "$declaration" =~ ^declare[[:space:]]+-[^[:space:]]*r ]]; then
        printf '\033[31m%s [ERROR] MY_STUDY_VAR_CHIP_SOC_TYPE is readonly; please use a Shell where it can be set.\033[0m\n' \
            "$(date '+%Y-%m-%d %H:%M:%S')" >&2
        return 1
    fi
    script_path=${BASH_SOURCE[0]}
    script_dir=${script_path%/*}
    [[ "$script_dir" != "$script_path" ]] || script_dir=.
    script_dir=$(cd -- "$script_dir" && pwd -P) || return 1
    if soc=$(python3 -B "$script_dir/_chip_env.py" "$@"); then
        if ! export MY_STUDY_VAR_CHIP_SOC_TYPE="$soc"; then
            return 1
        fi
    else
        return 1
    fi
    printf '%s [INFO] Environment variable set successfully: MY_STUDY_VAR_CHIP_SOC_TYPE=%s.\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" "$MY_STUDY_VAR_CHIP_SOC_TYPE"
}

if _msot_set_chip_soc_env "$@"; then
    unset -f _msot_set_chip_soc_env
    return 0
else
    case $? in
        2) unset -f _msot_set_chip_soc_env; return 2 ;;
        *) unset -f _msot_set_chip_soc_env; return 1 ;;
    esac
fi
