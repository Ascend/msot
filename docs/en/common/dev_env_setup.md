# Operator Tool Development Environment Setup Guide

## 1. Pulling the Image

> [!NOTE]
> Notes on the Compilation Environment
> Since glibc follows the principle of "backward compatibility" but not "forward compatibility," to ensure that the compiled executable can run on most operating systems, the build image typically uses an earlier version of the operating system.
> If a program built on a later operating system is deployed to an earlier environment, exceptions may occur. The dedicated build image for Scenario 2 was released around 2018 and is broadly compatible with current mainstream legacy runtime environments.
> However, this operating system version has limited functionalities (for example, it does not support VS Code remote access), so it is recommended only for final compilation and packaging. For daily development and debugging, use the newer image to improve efficiency and experience.

### Tips on Scenario Selection

For scenarios where compilation and execution only need to occur in a single environment without cross-OS version compatibility concerns, **Scenario 1** is recommended for maximum development efficiency.
Conversely, if the compiled software package needs to be deployed to a legacy operating system, **Scenario 2** should be selected. (It is recommended to first use the image from Scenario 1 to complete software debugging, ensure its stability, and then switch to the Scenario 2 image for final compilation, thereby achieving a balance between development efficiency and runtime compatibility.)

### Scenario 1: Development and Debugging in a Single Environment

Use the CANN official container image as the compilation environment. For image details, refer to [CANN Official Image Repository](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884).
Select an `openEuler` image similar to the following version: `9.0.0-xxx-openeuler24.03-py3.11` (where xxx should be filled in based on your Ascend AI processor model).
Taking Atlas A2 training products/Atlas A2 inference products as the example, the pull command is as follows:

```shell
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-beta.2-910b-openeuler24.03-py3.11
```

### Scenario 2: Packaging and Deployment for Legacy Operating Systems

Obtain the corresponding operator development and compilation Docker image from the Huawei CLOUD official container image repository based on your specific environment.

- **x86 architecture**:

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:x86_20260211_v01
```

- **Arm architecture**:

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:arm_20260211_v01
```

## 2. Starting the Container

### 2.1 Downloading the Container Startup Script

Run the following command to download:

```shell
cd ~
curl -fLO --retry 10 --retry-all-errors --retry-delay 3 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" https://raw.gitcode.com/Ascend/msot/raw/master/example/quick_start/public/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE]
> If the `--retry-all-errors` parameter is reported as non-existent, it indicates an outdated curl version. Remove this parameter and try again.
> If the download still fails after multiple attempts, it may be due to a CDN protection mechanism preventing automated scripts from scraping code. You can manually download the [ctr_in.py](../../../example/quick_start/public/ctr_in.py) file from the repository.

### 2.2 Executing the Startup Command

**Parameter Description:**

| Parameter | Description | Example |
| ---------------- | ------------------------------------ | --------------- |
| `CONTAINER_NAME` | Container name, which can be used to log in to the container later. Recommended format: `{purpose}_{personal_identifier}` | `op_dev_alice` |
| `USER_NAME` | Host username, used to mount the `$HOME` directory for data sharing | `alice` |
| `IMAGE` | Docker image ID or full name | `6df0c5bbc16f` |

**Command Format:**

```shell
python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>
```

**Execution Example:**

```shell
# Use image ID
python3 ~/ctr_in.py op_dev_alice alice 6df0c5bbc16f

# Use full image name
python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-beta.2-910b-openeuler24.03-py3.11
```

**Expected Output:**
After successful startup, you will enter the container. The terminal displays the command prompt inside the container, waiting for command input:

```text
Welcome to 5.10.0-60.139.0.166.oe2203.aarch64

System information as of time:  Fri Mar 20 06:46:56 UTC 2026
System load:    8.95
Memory used:    6.2%
Swap used:      55.4%
Usage On:       25%
Users online:   0

[root@localhost alice]#
```

> [!NOTE]
> **How to re-enter the container after exiting?**
>
> 1. Execute: `python3 ~/ctr_in.py op_dev_alice`. When only one parameter is passed, the script will perform the operation of entering an existing container and supports fuzzy matching of container names.
> 2. You can also use the native Docker command: `docker exec -it op_dev_alice bash`.

## 3. Environment Setup

### 3.1. Environment Configuration for Scenario 1

After entering the container, run the following command:

```shell
yum install ninja-build -y
yum install pigz -y
```

### 3.2 Environment Configuration for Scenario 2

Run the following command to write the CANN environment variable configuration to the `~/.bashrc` file to ensure it takes effect permanently:

```shell
echo "source /usr/local/Ascend/cann/set_env.sh" >> ~/.bashrc
source ~/.bashrc
```

## 4. FAQs

### 4.1 How to enter the password only once when it is prompted multiple times during dependency download?

You can configure and save Git credentials using the following command:

```shell
git config --global credential.helper store
```
