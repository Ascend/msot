#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_ai_soc_version.py - 昇腾 AI 处理器芯片型号检测工具

功能描述:
    本脚本用于自动检测当前环境中昇腾 NPU 芯片的型号信息，并生成相应的环境变量配置脚本。

主要功能:
    1. 通过 npu-smi 命令获取 NPU 芯片信息
    2. 解析芯片名称 (Chip Name) 和 NPU 标识 (NPU Name)
    3. 自动生成 shell 脚本，设置 MY_STUDY_VAR_CHIP_SOC_TYPE 环境变量
    4. 将环境变量追加到 ~/.bashrc 以实现持久化配置

使用方法:
    python get_ai_soc_version.py

依赖要求:
    - 已安装 CANN 软件包
    - npu-smi 命令可用

输出:
    - 生成 set_chip_env_var.sh 脚本文件
    - 执行 source set_chip_env_var.sh 即可应用环境变量
"""
import subprocess
import os
import re

def get_npu_id():
    try:
        result = subprocess.run(
            ["npu-smi", "info", "-l"],
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        print("Error: npu-smi command not found. Please ensure CANN is installed.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running 'npu-smi info -l': {e}")
        print(e.stderr)
        exit(1)

    match = re.search(r'NPU ID\s+:\s+(\d+)', result.stdout)
    if not match:
        print("Error: Failed to find 'NPU ID' in 'npu-smi info -l' output.")
        exit(1)
    return match.group(1)


def run_npu_smi():
    npu_id = get_npu_id()
    try:
        result = subprocess.run(
            ["npu-smi", "info", "-t", "board", "-i", npu_id, "-c", "0"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        print("Error: npu-smi command not found. Please ensure CANN is installed.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running npu-smi: {e}")
        print(e.stderr)
        exit(1)

def parse_chip_info(output):
    chip_name = None
    npu_id = None

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Chip Name"):
            # Example: Chip Name                      : 910B4
            match = re.search(r':\s*(\S+)', line)
            if match:
                chip_name = match.group(1)
        elif line.startswith("NPU Name"):
            # Example: NPU ID                         : 0
            match = re.search(r':\s*(\S+)', line)
            if match:
                npu_id = match.group(1)

    return chip_name, npu_id

def main():
    output = run_npu_smi()
    chip_name, npu_id = parse_chip_info(output)

    if not chip_name:
        print("Error: Failed to extract 'Chip Name' from npu-smi output.")
        exit(1)

    # Determine final chip type
    if npu_id and npu_id != "NA" and npu_id != "":
        chip_type = f"{chip_name}_{npu_id}"
        chip_type = chip_type.replace("Ascend", "")
    else:
        chip_type = chip_name

    # Generate shell script content
    shell_script_content = f"""echo add env var:MY_STUDY_VAR_CHIP_SOC_TYPE={chip_type}
echo append this env var into ~/.bashrc
export MY_STUDY_VAR_CHIP_SOC_TYPE={chip_type}
echo "export MY_STUDY_VAR_CHIP_SOC_TYPE={chip_type}" >> ~/.bashrc
"""

    script_path = "set_chip_env_var.sh"
    with open(script_path, "w") as f:
        f.write(shell_script_content)

    # Make it executable
    os.chmod(script_path, 0o755)

    print(f"Chip type detected: {chip_type}")
    print(f"Shell script generated: {os.path.abspath(script_path)}")
    print(f"To apply immediately, run: source {script_path}")

if __name__ == "__main__":
    main()