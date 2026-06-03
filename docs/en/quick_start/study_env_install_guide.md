# Ascend AI Operator Development Toolchain Learning Environment Installation Guide

<br>

>[!CAUTION] Note
>**Disclaimer**
>This document and related scripts are for learning purposes only and do not guarantee stability or security in production environments. Users must evaluate risks and assume corresponding responsibilities on their own.

## 1. Operator Tool Learning Environment Installation

You need to prepare a Linux server equipped with at least one Ascend NPU card, with the NPU driver and firmware already installed.

### 1.1 Operator Tool Installation

The Operator Tool is released as part of CANN and provides the following two installation methods:

1. **Containerized Runtime Environment**: Recommended method. It can be completed within 5 minutes when the Docker service is running normally. Please refer to the [CANN Container Environment Setup Guide](./cann_container_setup.md) for installation.
2. **Bare Metal or Virtual Machine Environment**: Installation is complex and time-consuming. Multi-user sharing can easily lead to conflicts and potentially difficult-to-resolve environmental issues. If you must use this type of environment, please refer to the [CANN Installation Official Documentation](https://www.hiascend.com/document/detail/en/canncommercial/800/quickstart/index/index.html) for installation; using a relatively newer version is sufficient.

### 1.2 Workspace Directory Initialization

**1. Creating Workspace**  
Create the `workspace` directory to store various files generated during example execution. The path is `~/ot_demo/workspace` (where "ot" is the abbreviation for Operator Tool):

```shell
mkdir -p ~/ot_demo/workspace
```

**2. Downloading Repository**  
Download to the `~/ot_demo` directory. After downloading, the example path is `~/ot_demo/msot/example`:

```shell
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

> Tip: If git download fails in the environment, you can directly download the compressed package from gitcode.com, manually upload it to the server, and ensure the directory structure is correct.

### 1.3 Obtaining the Chip SoC Model

Since the chip SoC model is frequently used in many subsequent commands and the method for obtaining it is relatively complex, it is obtained here uniformly and stored in the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` for easy reference later.

>[!CAUTION]Note  
>The environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` is only used for this quick start learning. Do not use this variable for commercial development.

#### 1.3.1 Automatically Obtaining the Chip SoC Model

If you want to quickly experience the tool, run the following command to automatically obtain and set the chip SoC model:

```shell
python3 ~/ot_demo/msot/example/quick_start/public/get_ai_soc_version.py
```

If the execution is successful, run as prompted:

```shell
source set_chip_env_var.sh
```

This script writes the chip SoC model (with the "Ascend" prefix removed, such as 910B4, 910_9392) into the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE`.

#### 1.3.2 Manually Obtaining the Chip SoC Model

If you want to learn about the concept and acquisition method of the chip SoC model, please refer to [Ascend Chip SoC Model Acquisition Method](get_chip_soc_type.md) to manually obtain the chip SoC model, and replace `<YOUR_CHIP_NAME>` in the following command with the value after removing the "Ascend" prefix (e.g., 910B4) before executing:

```shell
echo "export MY_STUDY_VAR_CHIP_SOC_TYPE=<YOUR_CHIP_NAME>" >> ~/.bashrc && source ~/.bashrc
```

>[!CAUTION] Note    
>The value of `MY_STUDY_VAR_CHIP_SOC_TYPE` is the value after removing the Ascend prefix:
>Correct values: 910B4, 910_9392;  
>Incorrect values: Ascend910B4, Ascend910_9392.

### 1.4 Installing Python Libraries

The operator project build depends on the following libraries. Please execute the following command to install them:

```shell
pip3 install -r ~/ot_demo/msot/example/quick_start/public/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ln -sf /usr/local/bin/python3 /usr/bin/python3
```

>[!NOTE] Note  
>Since the official website download speed is slow, the above command uses the Alibaba source for installation. If your environment cannot access the Alibaba source, or if you do not trust this source for security reasons, you can remove the -i xxx parameter to restore the default source.
