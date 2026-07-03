# Ascend CANN Container Environment Installation Guide

<!-- md-trans-meta sourceCommit=unknown translatedAt=2026-06-24T02:30:36.114Z pushedAt=2026-06-24T10:56:06.396Z -->

This guide is based on the **Ascend CANN official image** and helps you quickly set up an operator development environment for Ascend AI through Docker containerization.

## Prerequisites

Ensure the following environment is ready:

| Condition | Description | Verification Command |
| ----------------- | --------------------------------- | ----------------------- |
| Docker Engine | Installed and daemon running | `docker info` |

After meeting the above conditions, full deployment typically **completes within 5 minutes** (depending on network speed). If a CANN image already exists locally, startup can be **completed in seconds**.

## 1. Obtaining the CANN Development Image

> [!CAUTION]
> Operator development **must** use images with the `-devel` suffix (which include the complete compilation toolchain). Do not use ordinary runtime images.

### 1.1 Querying Local Images

Run the following command to check whether a CANN development image already exists:

```bash
docker images | grep cann | grep devel
```

Example output:

```text
REPOSITORY                                          TAG                                               IMAGE ID            CREATED             SIZE
swr.cn-south-1.myhuaweicloud.com/ascendhub/cann     9.0.0-910b-openeuler24.03-py3.11-devel            6df0c5bbc16f        2 weeks ago         11.9GB
```

If a suitable version already exists, you can skip directly to [Section 2: Starting the Container](#2-starting-the-container).

### 1.2 Pulling a CANN Image

#### 1.2.1 Obtaining the Image Download Command

1. Visit the [CANN Image Repository](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884), switch to the **"Image Download"** tab, and browse the list of available versions (you can filter using the search box on the right):

    ![image.png](https://raw.gitcode.com/user-images/assets/9310220/32504999-0da1-4595-8865-acd9a01cfd3b/image.png 'image.png')

2. Select an image version based on the following suggestions:

    | Option | Suggestion |
    | ----------- | ------------------------------------------------ |
    | **CANN Version** | If there are no special requirements, it is recommended to use the latest stable version |
    | **Chip Model** | Select based on the actual hardware (run `npu-smi info` to check) |
    | **Operating System** | Either openEuler or Ubuntu is acceptable |
    | **Development-Specific** | You should select a version with the `-devel` suffix, as this version includes the complete software environment required for operator development |

    > [!CAUTION]
    > You must use an image with the `-devel` suffix (e.g., `...-py3.11-devel`), otherwise custom operators cannot be compiled.

3. Click "Download Now" and copy the generated `docker pull` command.

    ![image.png](https://raw.gitcode.com/user-images/assets/9310220/0b35b9a5-b9c4-4c42-a25d-31432c6611d2/image.png 'image.png')

#### 1.2.2 Online Pull (Server with Internet Access)

Execute the copied command. An example is shown below (takes approximately 3–5 minutes, depending on network bandwidth and latency):

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
```

After the image pull is complete, go to [Section 2: Starting the Container](#2-starting-the-container).

#### 1.2.3 Offline Import (Server Without Internet Access)

If the server cannot directly access the HUAWEI CLOUD container image repository (for example, in an isolated network environment such as an enterprise intranet), follow these steps:

1. Pull the image on a host with internet access (ensure architecture matches x86/Arm):

   ```bash
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
   ```

2. Export as a tar file:

   ```bash
   docker save -o cann.tar swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
   ```

3. Transfer `cann.tar` to the server via a USB drive or transit network, and load it:

   ```bash
   docker load -i cann.tar
   ```

You can run the `docker images` command to check whether it has been loaded successfully. The loaded image is exactly the same as the one pulled online.

## 2. Starting the Container

### 2.1 Downloading the Container Start Script

Run the following command to download the startup script to the `HOME` directory:

```bash
cd ~ && curl -fLO --retry 10 --retry-all-errors --retry-delay 3 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" https://raw.gitcode.com/Ascend/msot/raw/master/example/quick_start/public/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE]
> If the `--retry-all-errors` parameter is reported as nonexistent, it indicates that the curl version is too old. You can remove this parameter and try again.  
> If the download still fails after multiple attempts, the CDN's anti-crawler protection mechanism may have been triggered. You can manually download the [ctr_in.py](../../../example/quick_start/public/ctr_in.py) file from the repository.  
> If your server is in an environment such as a corporate intranet that cannot directly connect to the external network, you can first download the file on the device currently accessing this document page, and then transfer it to the server via a USB drive or a transit network.

### 2.2 Executing the Startup Command

**Parameter Description:**

| Parameter | Description | Example |
| ------------------- | --------------------------------------------------------------------------- | ----------------- |
| `CONTAINER_NAME` | Container name, which can be used to log in to the container later. Suggested format: `{purpose}_{personal_id}` | `op_dev_alice` |
| `USER_NAME` | Host username, used to mount the `$HOME` directory for data sharing | `alice` |
| `IMAGE` | Docker image ID or full name | `6df0c5bbc16f` |

**Command Format:**

```bash
python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>
```

**Execution Example:**

```bash
# # Use image ID
python3 ~/ctr_in.py op_dev_alice alice 6df0c5bbc16f

# # Use image full name
python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
```

**Expected Output:**
After successful startup, you will directly enter the container, and the terminal will display the command prompt inside the container, waiting for command input:

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
> 1. Run: `python3 ~/ctr_in.py op_dev_alice`. When only one parameter is passed, the script will enter an existing container and supports fuzzy matching of container names.
> 2. You can also use the native Docker command: `docker exec -it op_dev_alice bash`.
