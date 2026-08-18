# Ascend AI Operator Development Toolchain Learning Environment Installation Guide

<br>

> [!CAUTION] Note
> This document and related scripts are for learning purposes only. Stability and security in production environments are not guaranteed. You must assess the related risks and assume full responsibility.

## 1. Prerequisites

Before starting the installation, ensure that the server meets the following requirements. Run all commands in this chapter on the **host machine**.

| Item | Requirement | Verification Method |
|------|-------------|---------------------|
| **Hardware compute power** | Linux server with at least 1 NPU (based on Ascend 910B/310P/A3 chips, **910B is recommended**), with the driver and firmware correctly installed | Run `npu-smi info` and confirm that the NPU status is normal. |
| **Container runtime** | Docker installed and running (version ≥ 18.x is recommended) | Run `docker ps`. If no errors are reported, the service started normally. |
| **Executing user** | Start the container with an ordinary user account. | Run `whoami`. It returns a non-`root` username. |
| **Script execution** | Python 3 installed (any version) | Run `python3 -V`. If version information is output, it is installed. |
| **Network communication** | curl installed (any version) | Run `curl -V`. If version information is output, it is installed. |

> 👉 After confirming that the prerequisites are met, if the environment has public network access, you can run all subsequent commands directly by **Copy/Paste** without manual input or concatenation, to avoid command execution failures caused by input errors.

## 2. Host Machine: Selecting and Pulling the CANN Image

> [!NOTE] Note
>
> - The Ascend AI operator development toolchain is released together with CANN. Installing CANN completes the toolchain deployment.
> - Because the operator compilation environment has complex dependencies, this tutorial **supports only** the CANN containerized deployment mode. Non-container environments such as bare-metal servers and virtual machines are not supported.

### 2.1 Automatically Identifying and Configuring Image Environment Variables Based on the Chip Model

Run the following command on the host machine (the command reads the NPU PCI ID, matches the image version, and writes the environment variable for use by subsequent processes):

```bash
source /dev/stdin <<< "$(dev_id=$(lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2); case "$dev_id" in 'd500' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-310p-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=310P";; 'd802' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=910B";; 'd803' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-a3-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=A3";; * ) echo "unset MY_STUDY_VAR_CANN_IMAGE MY_CHIP_NAME; echo >&2; echo -e '\033[31m[FAIL] Get device ID: $dev_id. Learning is not supported in the current environment.\033[0m' >&2";; esac)"
[ -n "$MY_STUDY_VAR_CANN_IMAGE" ] && echo -e "\e[32m[PASS] Successfully identified chip [$MY_CHIP_NAME] and auto-selected image:\n    $MY_STUDY_VAR_CANN_IMAGE\e[0m"
```

> [!NOTE] Note
>
> **Command Principle**  
> The command uses `lspci` to obtain the NPU PCI ID, automatically matches the official CANN image, and assigns the image address to the environment variable `MY_STUDY_VAR_CANN_IMAGE` for later use.  
> All images are the official CANN images published on Huawei Cloud AscendHub. For image details, see the [CANN Official Image Repository](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884).

If the command outputs `[PASS]`, the execution succeeded. If it outputs `[FAIL]`, possible causes are as follows:

1. The hardware is outside the scope supported by this tutorial: this learning environment supports only Ascend 910B, 310P, and A3 series chips. Switch to a compatible hardware environment and try again.
2. The underlying environment is abnormal: `lspci` is not installed, or the current user cannot query the NPU PCI ID using `lspci -n -D`. Contact the environment administrator to confirm the underlying environment.

### 2.2 Pulling the Image

Run the following command on the host machine:

```bash
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
```

If the pull fails because your environment is on a corporate intranet, see the solution in [Section 8.1](#81-obtaining-docker-images-in-an-isolated-intranet).

## 3. Host Machine: Downloading the Script and Starting the Container

### 3.1 Downloading the Container Startup Script

Run the following command on the host machine:

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

If you cannot download the script because of network restrictions, see the solution in [Section 8.2](#82-transferring-the-container-startup-script).

### 3.2 Starting the Container

Run the following command on the host machine. When prompted, confirm the container creation information and press Enter:

```bash
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

**Expected output**: If a message similar to the following appears and you stay at the root Shell prompt, the container started successfully:

```text
Welcome to 5.10.0-60.139.0.166.oe2203.aarch64

System information as of time:  Mon Jun 29 15:21:01 UTC 2026

System load:    8.44
Memory used:    1.5%
Swap used:      0%
Usage On:       27%
Users online:   0

[root@xxxxxx ~]#
```

If an error is reported or a container selection interface appears, see [Section 2.1](#21-automatically-identifying-and-configuring-image-environment-variables-based-on-the-chip-model) to confirm that the environment variable `MY_STUDY_VAR_CANN_IMAGE` is correct, and rerun the command.

> [!CAUTION] Note
>
> After you see the Shell prompt inside the container, run all commands in Chapters 4 to 6 **inside the container**.

## 4. In the Container: Cloning the Example Code Repository

In the container, clone the example code to the `~/ot_demo/msot` directory:

```bash
git clone https://gitcode.com/Ascend/msot.git -b 26.1.0 ~/ot_demo/msot
```

After cloning is complete, the example code is located at `~/ot_demo/msot/example`. If the clone fails because of network problems, see the solution in [Section 8.3](#83-transferring-the-example-code-repository).

## 5. In the Container: Setting the Chip SoC Model

Many subsequent commands need to reference the chip SoC model (system-on-a-chip model, used to identify the chip architecture). This section queries it uniformly and saves it to the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` for direct use later.  

Run the following command in the container:

```bash
echo 'export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace(\"Ascend\", \"\"))")' > /etc/profile.d/custom-env.sh && chmod +x /etc/profile.d/custom-env.sh && source /etc/profile.d/custom-env.sh && { [ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e '\033[31m[FAIL] Failed to set environment variable $MY_STUDY_VAR_CHIP_SOC_TYPE!\033[0m'; }
```

If `[PASS]` is displayed, the setting succeeded. If `[FAIL]` is displayed, it is usually because the CANN container was not deployed successfully, or you mistakenly ran this step on the host machine (outside the container). Confirm that you are inside the container and try again.

> [!CAUTION] Note
> The environment variables `MY_STUDY_VAR_CHIP_SOC_TYPE` and `MY_STUDY_VAR_CANN_IMAGE` apply only to this quick start tutorial. Do not use them in commercial development.

## 6. Installation Completion Self-Check

Run the following commands in the container to confirm that the environment required for the quick start is ready:

```bash
[ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e "\033[31m[FAIL] Missing environment variable MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m"
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] Example code repository OK\033[0m" || echo -e "\033[31m[FAIL] Example code repository missing\033[0m"
```

If all the preceding checks output `[PASS]`, the learning environment installation is complete. Return to the quick start document and continue with the subsequent operations.

<br>

## 7. Frequently Asked Questions (FAQ)

### 7.1 How Do I Re-enter the Container After Exiting?

Run either of the following commands on the host machine:

**Method 1 (recommended)**: Run `~/ctr_in.py` and select the target container interactively (if there is only one container, you enter it automatically).

**Method 2 (native command)**: Run `docker exec -it alice_YYMMDD_HHMMSS bash` (replace it with the actual container name).

### 7.2 What If a Permission Denied Error Occurs When Running Docker Commands?

The current user may not be added to the Docker user group. Run the following command on the host machine with root permissions:

```bash
sudo usermod -aG docker <username>
```

After running the command, log out and log in to the current user session again, or run `newgrp docker` to make the user group change take effect immediately. You are advised not to use the root identity for daily operations.

## 8. Solutions for Intranet Environments Without Public Network Access

### 8.1 Obtaining Docker Images in an Isolated Intranet

**Solution 1: Configuring a Docker Proxy and Pulling Directly**

This applies to most Linux distributions with Docker version ≥ 18 (compatibility is not guaranteed in all scenarios). If an exception occurs, adjust the settings based on the actual situation.

Edit the Docker service proxy configuration file `/etc/systemd/system/docker.service.d/http-proxy.conf`. An example is as follows (replace the username, password, proxy address, and port based on the actual environment):

```text
[Service]
Environment="HTTP_PROXY=http://username:password@proxy.example.com:8080"
Environment="HTTPS_PROXY=http://username:password@proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1,.example.com"
```

After saving the file, reload and restart the Docker service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

You can then run `docker pull` normally.

**Solution 2: Importing the CANN Image Offline**

If the proxy solution is not feasible, first run the commands in [Section 2.1](#21-automatically-identifying-and-configuring-image-environment-variables-based-on-the-chip-model) on the intranet NPU server to obtain the value of the environment variable `MY_STUDY_VAR_CANN_IMAGE` for the current chip model. Then copy the image name to a machine that has public network access and the same CPU architecture, and run the following commands:

```bash
docker pull <MY_STUDY_VAR_CANN_IMAGE>
docker save -o cann.tar <MY_STUDY_VAR_CANN_IMAGE>
```

After transferring `cann.tar` to the intranet server using a USB flash drive or other methods, run the following commands on the intranet server to load it:

```bash
docker load -i cann.tar
docker images | grep cann
```

After the load is complete, return to [Chapter 3](#3-host-machine-downloading-the-script-and-starting-the-container) to start the container.

### 8.2 Transferring the Container Startup Script

In a browser that can access the current webpage, enter the following link to download the `ctr_in.py` script, and manually copy it to the `~/` directory of the intranet server:

```text
https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py
```

After copying, run the following commands on the host machine of the intranet server:

```bash
cd ~
chmod +x ctr_in.py
ls -l ctr_in.py
```

After confirming that `ctr_in.py` exists and has execute permission, return to [Section 3.2](#32-starting-the-container) to start the container.

### 8.3 Transferring the Example Code Repository

In a browser that can access the current webpage, enter the following link. On the page, click the **Download ZIP** button to download the code repository package to your local machine:

```text
https://gitcode.com/Ascend/msot
```

Transfer the downloaded zip package to the `~` directory in the container of the intranet server (you can use methods such as the `docker cp` command, mounted directories, or network transfer to transfer it into the container).

Run the following command in the container to decompress the package. Replace `<MSOT_ZIP>` with the actual zip package file name:

```bash
unzip <MSOT_ZIP> -d ~/ot_demo
```

Then run the following commands to move the example code repository to the `~/ot_demo/msot` directory and confirm that the directory location is correct:

```bash
mv ~/ot_demo/msot-* ~/ot_demo/msot
ls ~/ot_demo/msot/example/quick_start
```

If the `ls` command reports no errors, the example code repository is synchronized. Then return to [Chapter 5](#5-in-the-container-setting-the-chip-soc-model) to set the chip SoC model.
