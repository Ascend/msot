# Ascend AI Operator Development Toolchain Learning Environment Setup Guide

> [!CAUTION]  
> This document and related scripts are for learning purposes only. Stability and security in production environments are not guaranteed. Users should assess risks and assume corresponding responsibilities on their own.

You need to prepare a Linux server equipped with at least one Ascend NPU card, with the NPU driver, firmware, and Docker service already installed.

## 1. Operator Development Toolchain Installation

👉 **[Key Installation Step] Strictly follow the [CANN Container Environment Setup Guide](./cann_container_setup.md) to complete the installation. It can be completed within 5 minutes when the Docker service is running normally.**

> [!NOTE]
> The Ascend AI operator development toolchain is released together with CANN, so installing CANN completes the installation. Due to the complex dependencies of the operator compilation environment, and to prevent environmental issues from affecting the learning experience, this tutorial requires the use of the CANN container environment and does not support non-containerized environments (such as bare metal or virtual machines).  

## 2. Workspace Creation and Code Repository Download

Create a `workspace` directory to store various files generated during the example execution process; clone the code repository to the `~/ot_demo` directory. After cloning, the example path will be `~/ot_demo/msot/example`:

```shell
mkdir -p ~/ot_demo/workspace
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

If `git` download is abnormal in the environment, you can directly download the repository archive from the GitCode website, manually upload it to the server, and ensure that the directory structure is consistent with the above.

## 3. Chip SoC Model Information Configuration

Since the chip SoC model information is frequently used in multiple subsequent commands, it is obtained and stored in the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` here for easy reference later.

> [!CAUTION]
> The environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` is only used for this quick start learning. Do not use this variable for commercial development.

Run the following command:

```shell
export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace('Ascend', ''))")
```
