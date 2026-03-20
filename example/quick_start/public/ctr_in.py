#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
"""
Start or enter Docker container with Ascend NPU device support.

Usage:
    python ctr_in.py <CONTAINER_NAME>                                    # Enter existing container
    python ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE_NAME>           # Create & enter (root)
    python ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE_NAME> nonroot   # Create & enter (current user)

Version: 1.0
"""

import json
import os
import shutil
import subprocess
import sys
import traceback

SCRIPT_NAME = os.path.basename(__file__)

USAGE_TEXT = f"""\
Usage:
    python {SCRIPT_NAME} <CONTAINER_NAME>                                    Enter an existing container
    python {SCRIPT_NAME} <CONTAINER_NAME> <USER_NAME> <IMAGE_NAME>           Create & enter (as root)
    python {SCRIPT_NAME} <CONTAINER_NAME> <USER_NAME> <IMAGE_NAME> nonroot   Create & enter (as current user)

Arguments:
    CONTAINER_NAME    Name (or keyword) of the Docker container
    USER_NAME         Host username for home directory binding
    IMAGE_NAME        Docker image name or ID (e.g., quay.io/ascend/vllm-ascend:v0.12.0rc1)
    nonroot           Optional 4th arg: run container as current user (uid:gid) instead of root

Examples:
    python {SCRIPT_NAME} my-ascend-container
    python {SCRIPT_NAME} my-ascend-container sam quay.io/ascend/vllm-ascend:v0.12.0rc1
    python {SCRIPT_NAME} my-ascend-container sam quay.io/ascend/vllm-ascend:v0.12.0rc1 nonroot

Description:
    With 1 argument    - enter an existing container by exact name or keyword search.
    With 3 arguments   - create a new container with Ascend NPU device support (as root), then enter it.
    With 4 arguments   - same as above, but run as current host user instead of root.
"""


def usage() -> None:
    print(USAGE_TEXT)
    sys.exit(1)


def run_cmd(cmd: list[str], *, check: bool = True, capture: bool = True, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=capture, text=True, **kwargs)


def check_docker() -> None:
    if shutil.which("docker") is None:
        print("Error: Docker is not installed", file=sys.stderr)
        sys.exit(1)

    result = run_cmd(["docker", "version", "--format", "{{.Server.Version}}"], check=False)
    if result.returncode != 0:
        print("Error: Docker daemon is not running", file=sys.stderr)
        sys.exit(1)


def validate_user_home(user_name: str) -> None:
    user_home = f"/home/{user_name}"
    if not os.path.isdir(user_home):
        print(f"Error: User home directory '{user_home}' does not exist", file=sys.stderr)
        sys.exit(1)


def check_image(image_name: str) -> None:
    result = run_cmd(["docker", "image", "inspect", image_name], check=False)
    if result.returncode != 0:
        print(f"Error: Image '{image_name}' not found. Please pull it first.", file=sys.stderr)
        sys.exit(1)


def resolve_image_id(image_ref: str) -> str:
    """If image_ref is a short/full ID (hex only), resolve it to repo:tag via inspect."""
    stripped = image_ref.removeprefix("sha256:")
    if not all(c in "0123456789abcdef" for c in stripped) or len(stripped) < 12:
        return image_ref

    result = run_cmd(["docker", "image", "inspect", "--format",
                       "{{range .RepoTags}}{{.}}\n{{end}}", image_ref], check=False)
    if result.returncode != 0:
        return image_ref

    short_id = stripped[:12]
    tags = [t for t in result.stdout.strip().splitlines() if t]
    if tags:
        return f"{tags[0]} [{short_id}]"
    return f"{image_ref} (untagged)"


def get_all_containers(names_filter: set[str]) -> list[tuple[str, str]]:
    """Return list of (name, image) for all containers.

    If names_filter is provided, only resolve image IDs for containers in the set.
    """
    result = run_cmd(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Image}}"])
    containers = []
    for line in result.stdout.strip().splitlines():
        if not line:
            continue
        parts = line.split("\t", 1)
        name = parts[0]
        raw_image = parts[1] if len(parts) > 1 else ""
        if names_filter is None or name in names_filter:
            image = resolve_image_id(raw_image)
        else:
            image = raw_image
        containers.append((name, image))
    return containers

def _fmt_size(bytes_val) -> str:
    if not bytes_val or bytes_val <= 0:
        return "unlimited"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"


def show_container_details(container_name: str):
    """Show a detailed info table for a container (~20 key items)."""
    try:
        result = run_cmd(["docker", "inspect", container_name], check=False)
        if result.returncode != 0:
            print(f"Error: cannot inspect container '{container_name}'", file=sys.stderr)
            return

        info = json.loads(result.stdout)[0]
        state = info.get("State", {})
        config = info.get("Config", {})
        host_cfg = info.get("HostConfig", {})
        net_settings = info.get("NetworkSettings", {})

        privileged = host_cfg.get("Privileged", False)
        net_mode = host_cfg.get("NetworkMode", "")
        pid_mode = host_cfg.get("PidMode", "")
        ipc_mode = host_cfg.get("IpcMode", "")
        restart_pol = host_cfg.get("RestartPolicy", {}).get("Name", "no")
        oom_disabled = host_cfg.get("OomKillDisable", False)
        readonly_root = host_cfg.get("ReadonlyRootfs", False)
        mem_limit = host_cfg.get("Memory", 0)
        cpu_shares = host_cfg.get("CpuShares", 0)
        nano_cpus = host_cfg.get("NanoCpus", 0)

        mounts = info.get("Mounts", [])
        mount_lines = [
            f"{m.get('Source', '?')} -> {m.get('Destination', '?')}"
            + (":ro" if m.get("RW") is False else "")
            for m in mounts
        ]

        ports_raw = net_settings.get("Ports") or {}
        port_lines = []
        for cport, bindings in ports_raw.items():
            if bindings:
                for b in bindings:
                    port_lines.append(f"{b.get('HostIp', '0.0.0.0')}:{b.get('HostPort')} -> {cport}")
            else:
                port_lines.append(cport)
        ports_str = ", ".join(port_lines) if port_lines else "none"

        cap_add = host_cfg.get("CapAdd") or []
        cap_drop = host_cfg.get("CapDrop") or []
        devices = host_cfg.get("Devices") or []
        device_str = ", ".join(d.get("PathOnHost", "?") for d in devices[:5])
        if len(devices) > 5:
            device_str += f" ... (+{len(devices) - 5} more)"

        env_count = len(config.get("Env") or [])
        image_name = config.get("Image", "N/A")
        entrypoint = " ".join(config.get("Entrypoint") or []) or "N/A"
        cmd = " ".join(config.get("Cmd") or []) or "N/A"

        cpu_display = f"{nano_cpus / 1e9:.2f} cores" if nano_cpus else (str(cpu_shares) if cpu_shares else "unlimited")

        rows = [
            # ── 基本信息 ──
            ("Container Name",    info.get("Name", "").lstrip("/")),
            ("Container ID",      info.get("Id", "")[:12]),
            ("Hostname",          config.get("Hostname", "N/A")),
            ("Image",             image_name),
            ("Created",           info.get("Created", "N/A")[:19].replace("T", " ")),
            ("WorkingDir",        config.get("WorkingDir", "/") or "/"),
            None,
            # ── 运行状态 ──
            ("Status",            state.get("Status", "unknown")),
            ("StartedAt",         state.get("StartedAt", "N/A")[:19].replace("T", " ")),
            ("RestartCount",      str(info.get("RestartCount", 0))),
            ("Restart Policy",    restart_pol),
            None,
            # ── 网络 ──
            ("Network Mode",      net_mode),
            ("Ports",             ports_str),
            None,
            # ── 资源限制 ──
            ("CPU Limit",         cpu_display),
            ("Memory Limit",      _fmt_size(mem_limit)),
            ("OOM Kill Disabled", str(oom_disabled)),
            ("Devices",           device_str or "none"),
            None,
            # ── 安全与隔离 ──
            ("Privileged",        str(privileged)),
            ("PID Mode",          pid_mode or "container"),
            ("IPC Mode",          ipc_mode or "private"),
            ("ReadOnly RootFS",   str(readonly_root)),
            ("Capabilities Add",  ", ".join(cap_add) if cap_add else "none"),
            ("Capabilities Drop", ", ".join(cap_drop) if cap_drop else "none"),
            None,
            # ── 存储与设备 ──
            ("Mounts",            f"{len(mount_lines)} total:" if mount_lines else "none"),
            None,
            # ── 进程配置 ──
            ("Entrypoint",        entrypoint),
            ("Cmd",               cmd),
            ("Env Var Count",     str(env_count)),
        ]

        data_rows = [r for r in rows if r is not None]
        key_w = max(len(r[0]) for r in data_rows)
        val_w = max(min(len(r[1]), 70) for r in data_rows)
        total_w = key_w + val_w + 7

        print()
        print("=" * total_w)
        print(f"  Container Details: {container_name}")
        print("=" * total_w)
        for row in rows:
            if row is None:
                print(f"  {'─' * (total_w - 2)}")
            else:
                key, val = row
                display_val = val if len(val) <= 70 else val[:67] + "..."
                print(f"  {key:<{key_w}}  │  {display_val}")
                if key == "Mounts" and mount_lines:
                    for ml in mount_lines:
                        mv = ml if len(ml) <= 70 else ml[:67] + "..."
                        print(f"  {'':<{key_w}}  │    {mv}")
        print("=" * total_w)
        print()
    except Exception as e:
        print(f"Error: cannot show container details for '{container_name}': {e}", file=sys.stderr)
        return


def prompt_existing_container(container_name: str):
    """If the container already exists, prompt the user to enter it or recreate it.

    Returns:
        None            - container does not exist, proceed with creation
        "enter"         - user chose to enter the existing container
        "recreate"      - user chose to delete and recreate
    """
    names = [n for n, _ in get_all_containers(names_filter=set())]
    if container_name not in names:
        return None

    show_container_details(container_name)
    print("=" * 58)
    print(f"*** Container '{container_name}' already exists! ***")
    print("=" * 58)
    print()
    print("  [1] Enter the existing container")
    print("  [2] Delete it and create a new one")
    print("  [q] Quit")
    print()

    while True:
        choice = input("Please select (1/2/q): ").strip().lower()
        if choice == "1":
            return "enter"
        if choice == "2":
            try:
                run_cmd(["docker", "rm", "-f", container_name])
            except Exception as _:
                print(traceback.format_exc())
                sys.exit(1)
            print(f"Removed existing container '{container_name}'")
            return "recreate"
        if choice in ("q", "quit"):
            print("Aborted")
            sys.exit(0)
        print("Invalid selection, please try again.")


def ensure_container_running(container_name: str) -> None:
    """Start the container if it is not already running."""
    print(f"Ensure container '{container_name}' is running...")
    result = run_cmd(["docker", "inspect", "-f", "{{.State.Running}}", container_name])
    if result.stdout.strip() != "true":
        print(f"Container '{container_name}' is not running, starting it...")
        try:
            run_cmd(["docker", "start", container_name], capture=False)
        except Exception as _:
            print(traceback.format_exc())
            sys.exit(1)
    print(f"Container '{container_name}' is running.")

def enter_container(container_name: str) -> None:
    ensure_container_running(container_name)
    show_container_details(container_name)
    print(f"Entering container '{container_name}'...")

    exec_cmd = ["docker", "exec", "-it"]
    result = run_cmd(["docker", "inspect", "-f", "{{.Config.User}}", container_name], check=False)
    container_user = result.stdout.strip() if result.returncode == 0 else ""
    if container_user:
        exec_cmd.extend(["-u", container_user])

    exec_cmd.extend([container_name, "bash"])
    os.execvp("docker", exec_cmd)


def resolve_container(keyword: str) -> str:
    """Resolve a keyword to an exact container name, interactively if needed."""
    all_containers = get_all_containers(names_filter=set())

    all_names = [n for n, _ in all_containers]

    if keyword in all_names:
        return keyword

    matched_names = set(n for n in all_names if keyword in n)

    if not matched_names:
        print(f"Error: No container matching '{keyword}' found", file=sys.stderr)
        sys.exit(1)

    # Resolve image info only for matched containers
    matched_raw = [(n, img) for n, img in all_containers if n in matched_names]
    matches = [(n, resolve_image_id(img)) for n, img in matched_raw]

    if len(matches) == 1:
        print(f"Found container: {matches[0][0]}  (image: {matches[0][1]})")
        return matches[0][0]

    print(f"Multiple containers match '{keyword}':")
    max_name_len = max(len(name) for name, _ in matches)
    idx_width = len(str(len(matches)))
    for idx, (name, image) in enumerate(matches, 1):
        print(f"  [{idx:0>{idx_width}}] {name:<{max_name_len}}  (image: {image})")
    print(f"  [{'q':>{idx_width}}] quit")

    while True:
        choice = input(f"Select a container (1-{len(matches)}/q): ").strip().lower()
        if choice in ("q", "quit"):
            print("Aborted")
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice) - 1][0]
        print("Invalid selection, please try again.")


def start_container(container_name: str, user_name: str, image_name: str,
                    nonroot: bool = False) -> None:
    uid, gid = os.getuid(), os.getgid()
    run_as = f"{uid}:{gid}" if nonroot else "root"
    print(f"Begin to start container: {container_name}")
    print(f"User: {user_name}  (run as: {run_as})")
    print(f"Image: {image_name}")
    print("-" * 40)

    cmd = [
        "docker", "run", "-itd",
        f"--name={container_name}",
        f"--hostname={container_name.rsplit('_', 1)[0].replace('.', '_')}",
        "--net=host",
        "--privileged=true",
        "--device=/dev/davinci_manager",
        "--device=/dev/hisi_hdc",
        "--device=/dev/devmm_svm",
        "--entrypoint=bash",
        "-w", f"/home/{user_name}",
        "-v", f"/home/{user_name}:/home/{user_name}",
        "-v", "/usr/local/Ascend/driver:/usr/local/Ascend/driver:ro",
        "-v", "/usr/local/dcmi:/usr/local/dcmi:ro",
        "-v", "/usr/local/bin/npu-smi:/usr/local/bin/npu-smi:ro",
        "-v", "/etc/ascend_install.info:/etc/ascend_install.info:ro",
        "-v", "/usr/local/sbin:/usr/local/sbin:ro",
    ]

    if nonroot:
        cmd.extend([
            "--user", f"{uid}:{gid}",
            "-e", f"HOME=/home/{user_name}",
            "-v", "/etc/passwd:/etc/passwd:ro",
            "-v", "/etc/group:/etc/group:ro",
        ])

    cmd.append(image_name)

    result = run_cmd(cmd, check=False, capture=False)
    if result.returncode == 0:
        print("-" * 40)
        print(f"Container '{container_name}' started successfully.\n")
    else:
        print("Failed to start container", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    try:
        args = sys.argv[1:]

        if not args or args[0] in ("-h", "--help"):
            usage()

        check_docker()

        if len(args) == 1:
            container_name = resolve_container(args[0])
            enter_container(container_name)

        elif len(args) in (3, 4):
            container_name, user_name, image_name = args[0], args[1], args[2]
            nonroot = len(args) == 4

            validate_user_home(user_name)
            action = prompt_existing_container(container_name)

            if action == "enter":
                enter_container(container_name)
            else:
                check_image(image_name)
                start_container(container_name, user_name, image_name, nonroot=nonroot)
                enter_container(container_name)

        else:
            print(f"Error: Expected 1, 3, or 4 arguments, got {len(args)}", file=sys.stderr)
            usage()
    except Exception as _:
        print(traceback.format_exc(), file=sys.stderr)


if __name__ == "__main__":
    main()

