#!/usr/bin/env python3
"""Private implementation for quick-start preparation, never a tool-command proxy.

Copyright (c) 2026 Huawei Technologies Co., Ltd.
Licensed under Mulan PSL v2. See the repository LICENSE.
"""
import argparse
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from _files import PreparationError, apply_changes, check_copy, directory_lock, read_file, safe_path
from _project import prepare_add_demo, prepare_mode, restore_demo


EXAMPLES = Path(__file__).resolve().parent.parent


def prepare_sample(sample, destination):
    relative = {"mskpp": "mskpp/mskpp_demo.py", "opgen": "msopgen/msopgen_demo.json"}[sample]
    source = EXAMPLES / relative
    content = read_file(source)
    destination = safe_path(destination)
    with directory_lock(destination):
        target = destination / source.name
        check_copy(target, content)
        apply_changes({target: content}, destination / ".msot-pending.json")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("{} [INFO] Prepare sample successful, sample path is: {}.".format(timestamp, target))


def check_environment(task):
    """Read-only prerequisite checks; command presence is not business validation."""
    failures = []

    def log(message, level="INFO", color=None):
        line = "{} [{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message)
        if color:
            line = color + line + "\033[0m"
        print(line)

    def report(ok, message, failure_reason):
        if not ok:
            message += "; reason: " + failure_reason
        color = None if ok else "\033[31m"
        log("[{}] {}".format("PASS" if ok else "FAIL", message), "INFO" if ok else "ERROR", color)
        if not ok:
            failures.append(message)

    log("Starting to check the environment...")
    if task == "core":
        report(Path("/.dockerenv").is_file(), "standard container marker /.dockerenv",
               "container marker is missing; please run inside the documented CANN container.")
        for name in ("ASCEND_HOME_PATH", "ATB_HOME_PATH", "MY_STUDY_VAR_CHIP_SOC_TYPE"):
            report(bool(os.environ.get(name, "").strip()), "environment variable " + name,
                   "variable is unset or empty; please configure it using the installation guide.")
        assets = ("mskpp/mskpp_demo.py", "msopgen/msopgen_demo.json",
                  "msopgen/code/op_kernel/add_custom.cpp", "msopgen/caller/run.sh")
        report(EXAMPLES.is_dir() and all((EXAMPLES / name).is_file() for name in assets),
               "sample repository and required assets: " + str(EXAMPLES),
               "required sample files are missing; please use a complete msOT checkout.")
        for name in ("msopgen", "mssanitizer", "msdebug", "msopprof"):
            report(shutil.which(name) is not None, "command exists: " + name,
                   "command not found in PATH; please check the CANN installation and environment setup.")
    else:
        probe = shutil.which("npu-smi")
        if probe is None:
            report(False, "chip probe failed", "npu-smi was not found in PATH; check the driver tools")
        else:
            try:
                result = subprocess.run([probe, "info", "-m"], capture_output=True,
                                        text=True, timeout=15, errors="replace")
                chips = list(dict.fromkeys(re.findall(r"\bAscend\s*([A-Za-z0-9]+)\b", result.stdout)))
                if result.returncode:
                    report(False, "chip probe failed", "npu-smi exited with code {}".format(result.returncode))
                elif not chips:
                    report(False, "chip probe failed", "no recognized Ascend chip model in npu-smi output")
                else:
                    supported = all(re.fullmatch(r"910B[0-9]*", chip) for chip in chips)
                    report(supported, "detected chips: {}; {}".format(
                        ", ".join(chips), "910B meets the requirements." if supported else "unsupported for this msKPP tutorial"),
                        "this msKPP tutorial requires Ascend 910B-series chips")
            except subprocess.TimeoutExpired:
                report(False, "chip probe failed", "npu-smi did not respond within 15 seconds")
            except OSError as error:
                report(False, "chip probe failed", "could not execute npu-smi: " + str(error))
    log("Environment check {}, summary {} failure(s).".format(
        "failed" if failures else "successful", len(failures)), "ERROR" if failures else "INFO")
    return int(bool(failures))


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check-env", prog="bash check_env.sh", help="Check prerequisites without changing the environment",
                                allow_abbrev=False)
    check.add_argument("--task", choices=("core", "mskpp"), required=True)
    sample = commands.add_parser("prepare-sample", prog="bash prepare_sample.sh",
                                 help="Copy a sample input without executing it", allow_abbrev=False)
    sample.add_argument("--sample", choices=("mskpp", "opgen"), required=True)
    sample.add_argument("--dest", required=True, type=Path)
    assembly = commands.add_parser("prepare-add-demo", prog="bash prepare_add_demo.sh",
                                   help="Assemble a reviewed generated teaching project",
                                   allow_abbrev=False)
    assembly.add_argument("--project", required=True, type=Path)
    mode = commands.add_parser("prepare-mode", prog="bash prepare_mode.sh",
                               help="Prepare compilation options and an explicit teaching fixture",
                               allow_abbrev=False)
    mode.add_argument("--project", required=True, type=Path)
    mode.add_argument("--mode", choices=("sanitizer", "debug", "profile"), required=True)
    mode.add_argument("--fixture", choices=("oob",))
    restore = commands.add_parser("restore-demo", prog="bash restore_demo.sh",
                                  help="Restore managed source files, not deployed artifacts",
                                  allow_abbrev=False)
    restore.add_argument("--project", required=True, type=Path)
    return parser


def main(argv=None):
    args = make_parser().parse_args(argv)
    try:
        if args.command == "check-env":
            return check_environment(args.task)
        if args.command == "prepare-sample":
            prepare_sample(args.sample, args.dest)
        elif args.command == "prepare-add-demo":
            prepare_add_demo(args.project)
        elif args.command == "prepare-mode":
            prepare_mode(args.project, args.mode, args.fixture)
        else:
            restore_demo(args.project)
        return 0
    except (PreparationError, OSError, UnicodeError) as error:
        print("[FAIL] " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
