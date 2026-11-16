"""Query the chip model and prepare optional quick-start login configuration.

Copyright (c) 2026 Huawei Technologies Co., Ltd.
Licensed under Mulan PSL v2. See the repository LICENSE.
"""
import argparse
from datetime import datetime
import errno
from pathlib import Path
import re
import subprocess
import sys

from _files import PreparationError, apply_changes, check_copy, directory_lock, safe_path


PROFILE_FILE = Path("/etc/profile.d/custom-env.sh")
PROFILE_CONTENT = (
    'export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c '
    '"import acl; print(acl.get_soc_name().replace(\\"Ascend\\", \\"\\"))")\n'
).encode("utf-8")


def query_chip_soc():
    try:
        result = subprocess.run([sys.executable, "-B", "-c", "import acl; print(acl.get_soc_name())"],
                                capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired as error:
        raise PreparationError("Chip SoC query timed out after 15 seconds; please check the CANN environment.") from error
    except OSError as error:
        raise PreparationError("Could not start the chip SoC query: " + str(error)) from error
    if result.returncode:
        detail = result.stderr.strip().splitlines()
        reason = detail[-1] if detail else "query exited with code {}".format(result.returncode)
        raise PreparationError("Chip SoC query failed; please check Python acl and the CANN environment: " + reason)
    match = re.fullmatch(r"Ascend([A-Za-z0-9][A-Za-z0-9_-]*)", result.stdout.strip())
    if match is None:
        raise PreparationError("Chip SoC query returned an empty or unrecognized model; no environment variable was set.")
    return match.group(1)


def persist_profile(path):
    path = safe_path(path)
    pending = safe_path(path.parent / ".msot-chip-env-pending.json")
    lock = safe_path(path.parent / ".msot-prepare.lock")
    if pending.exists():
        raise PreparationError("Unfinished environment transaction; please inspect: " + str(pending))
    if lock.exists():
        raise PreparationError("Preparation lock exists; please inspect it before retrying: " + str(lock))
    # Detect readable conflicts before trying to create a lock in a protected directory.
    check_copy(path, PROFILE_CONTENT)
    if path.is_file():
        return  # Reuse identical content without requiring directory write permission.
    with directory_lock(path.parent):
        check_copy(path, PROFILE_CONTENT)
        apply_changes({path: PROFILE_CONTENT}, pending)


def log(level, message):
    line = "{} [{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message)
    if level == "ERROR":
        line = "\033[31m" + line + "\033[0m"
    print(line, file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--session-only", action="store_true", help="Set only the current Shell; do not access a profile file")
    args = parser.parse_args(argv)
    try:
        soc = query_chip_soc()
        if not args.session_only:
            try:
                persist_profile(PROFILE_FILE)
            except OSError as error:
                if not (isinstance(error, PermissionError) or error.errno == errno.EROFS):
                    raise
                log("WARNING", "Cannot persist environment to {} ({}); continuing with current-session setup only. "
                    "Please run source again in each new Shell.".format(PROFILE_FILE, error))
            else:
                log("INFO", "Environment configuration is available at: {}.".format(PROFILE_FILE))
        # Only the validated value goes to stdout for the sourced Shell to capture.
        print(soc)
        return 0
    except (PreparationError, OSError, UnicodeError) as error:
        log("ERROR", str(error))
        return 1


if __name__ == "__main__":
    sys.exit(main())
