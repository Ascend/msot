# Ascend CANN Installation Guide for Container Environment 

<br>

This guide is based on the **Ascend CANN official image** and helps you quickly set up an Ascend AI operator development environment through Docker containerization.

> [!CAUTION] Note    
> **Disclaimer**
> This document and related scripts are for learning and reference only. They do not guarantee stability or security in production environments. Users must evaluate the risks and assume corresponding responsibilities.

## Prerequisites

Before you begin, ensure that the following environment is ready:

| Condition | Description | Verification Command |
| ------------- | --------------- | -------------- |
| Docker engine | Installed and the daemon is running | `docker info` |
| Network connectivity | Accessible to the Huawei Cloud image repository for pulling images and downloading scripts | `ping swr.cn-south-1.myhuaweicloud.com` |

After meeting the above prerequisites, completing the environment setup and starting the container as described in this document typically takes less than **5 minutes** (depending on network speed). If a CANN image is locally available, it can be completed in **seconds**.

<br>

## 1. Preparing the Image

### 1.1 Querying Local Images

Run the following command to query existing CANN images in the current environment:

```shell
docker images | grep cann
```

If the returned result contains a CANN image, an example output is as follows:

```text
REPOSITORY                                          TAG                                               IMAGE ID            CREATED             SIZE
swr.cn-south-1.myhuaweicloud.com/ascendhub/cann     8.5.1-910b-openeuler24.03-py3.11                  6df0c5bbc16f        2 weeks ago         17.1GB
```

If a suitable version already exists, you can directly skip to [Section 2: Starting the Container](#2-starting-the-container).

### 1.2 Pulling a CANN Image

If no local image is available, follow the steps below.

**Step 1** Visit the [CANN Image Repository](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884), switch to the **"Image Versions"** tab, and browse the list of available versions:

![image.png](https://raw.gitcode.com/user-images/assets/8763895/f2a0ae4f-4a7a-4c0e-ada9-ec4a0ab71403/image.png 'image.png')

**Step 2** Select an image version based on the following suggestions:

| Option          | Suggestion                                               |
| ----------- | ------------------------------------------------ |
| **CANN Version** | If no special requirements exist, it is recommended to select the latest stable version.                                |
| **Chip Model**    | Select based on the actual hardware (run `npu-smi info` to check). |
| **Operating System**    | Either openEuler or Ubuntu is acceptable; openEuler is recommended.               |

**Step 3** Copy the full image version number (for example: 8.5.1-910b-openeuler24.03-py3.11) and assemble the pull command in the following format:

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:<image version>
```

Execution example (takes approximately 3–5 minutes, depending on network conditions):

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11
```

> [!NOTE] Note    
> **Why is the image name (swr.cn-south-1.myhuaweicloud.com/ascendhub/cann) so long?**    
> Because the full path format includes the complete registry address, allowing direct pulling without additional Docker registry configuration, enabling out-of-the-box use.

<br>

## 2. Starting the Container

### 2.1 Downloading the Container Startup Script

Run the following command to download:

```shell
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

### 2.2 Running the Start Command

**Parameters:**

| Parameter | Description | Example |
| ---------------- | ------------------------------------ | --------------- |
| `CONTAINER_NAME` | Container name, which can be used to log in to the container later. Recommended format: `{Purpose}_{ID}` | `op_dev_alice` |
| `USER_NAME` | Username on the host machine, used to mount the `$HOME` directory for data sharing. | `alice` |
| `IMAGE` | Docker image ID or full name. | `6df0c5bbc16f` |

**Command Format:**

```shell
python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>
```

**Example:**

```shell
# Use the image ID.
python3 ~/ctr_in.py op_dev_alice alice 6df0c5bbc16f

# Use the image full name.
python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11
```

**Expected Output:**    
After a successful start, you will directly enter the container. The terminal will display the command prompt inside the container, waiting for command input:

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

> [!NOTE] Note    
> **How to re-enter the container after exiting?**
>
> 1. Execute: `python3 ~/ctr_in.py op_dev_alice`. When only one parameter is passed, the script will perform the operation of entering an existing container and supports fuzzy matching of container names.
> 2. You can also use the native Docker command: `docker exec -it op_dev_alice bash`.
