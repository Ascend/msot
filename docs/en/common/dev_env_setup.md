# MindStudio Tool Development Environment Setup Guide

<br>

This document describes how to set up a standardized container environment for MindStudio tool development tasks such as compilation and unit testing (UT).

## 1. Method Selection

MindStudio tools support two ways to install the development environment. Choose the appropriate one based on your repository:

| Method | Applicable Condition | Description |
| --- | --- | --- |
| **Dev Containers** | The repository root directory contains a `.devcontainer` directory | Works out of the box. For details, refer to the README in the `.devcontainer` directory of the repository. |
| **CLI container environment (general method)** | Repositories of all Linux CLI tools | This is the method described in the following sections of this document. |

> [!NOTE] Note
>
> If the repository already has a `.devcontainer` directory configured, you are advised to use Dev Containers first, as it is the most efficient. Otherwise, set up the CLI container environment as described in the following sections.

## 2. Prerequisites

Ensure that the following dependencies are installed and running properly:

| Dependency | Description | Verification Command |
| --- | --- | --- |
| **Docker Engine** | Installed and the service is running | Run `docker ps`. If no error is reported, the service started properly. |
| **Python 3** | Installed on the host machine (any 3.x version) | Run `python3 -V`. Version information in the output indicates that Python is installed. |

> If a permission denied error occurs when you run `docker ps`, refer to [FAQ 7.1](#71-what-should-i-do-if-a-permission-denied-error-occurs-when-running-docker-commands).

## 3. Host Machine: Pulling the Dedicated Build Image

Pull the MindStudio build image from the Huawei Cloud image repository. You are advised to use the following image based on the openEuler base system, which is consistent with the CI build system:

```bash
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.2.0-0801
```

If you have special requirements for the Ubuntu system, you can also pull the following Ubuntu-based image, which is only for personal development and debugging:

```bash
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.2.0-0801-ubuntu22.04
```

> [!NOTE] Note
>
> If you need to build the image yourself, for example, to customize the content or troubleshoot layers, refer to the [MindStudio Unified Build Image Creation Guide](./docker_image_build_guide.md).

If pulling fails, refer to [FAQ 7.2](#72-what-should-i-do-if-image-pulling-fails).

## 4. Host Machine: Downloading the Container Startup Script

Download the helper script for automatically creating and configuring containers, and grant it execute permissions:

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE] Note
>
> The `ctr_in.py` script is powerful and can serve as a general-purpose tool for routine container operations. View its specific functions and usage with the `--help` parameter.

## 5. Host Machine: Starting and Entering the Build Container

Run the command as a **regular user**. Running it as root does not mount directories automatically, which reduces development efficiency. The script automatically completes directory mounting, user mapping, and environment initialization. The following is an example command:

```bash
~/ctr_in.py swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.2.0-0801
```

> [!CAUTION] Caution
>
> This image is **only for compilation and does not support running NPU programs**. The reason is that running a CANN container requires root permissions, and compilation generates a large number of root-owned files that pollute the `HOME` directory. In addition, the runtime libraries are heavily trimmed to control the image size.
>
> If you need to run NPU programs, you are advised to use the following **dual-terminal mode** development method. Both terminals share the `HOME` directory. Therefore, compilation, running, and the host machine are three separate environments that do not interfere with each other, which improves development efficiency:
>
> **Terminal 1 (compilation)**: Start the container of this build image, and the build artifacts are output to the `HOME` directory.
>
> **Terminal 2 (running)**: Start the official CANN runtime container, and read and execute files from the `HOME` directory. The following is an example startup command. For the specific version and other information, refer to the [official CANN image repository](https://www.hiascend.com/en/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884):
>
> ```bash
> ~/ctr_in.py swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12
> ```

### Expected Output

After the command runs, the terminal automatically switches to the interactive shell in the container and displays a MindStudio welcome screen similar to the following, indicating that the container has started and you have entered it successfully:

```text
=================================================================
           >>>>>   MindStudio Build Environment   <<<<<
    THE END-TO-END TOOLCHAIN TO UNLEASH HUAWEI ASCEND COMPUTE
=================================================================
  OS/Arch   : openEuler 24.03 (LTS-SP3) | x86_64
  Toolchain : GCC 11.2.0 | glibc >= 2.17 | CANN 9.1.0
              ccache   : /home/alice/.cache/ccache (persistent)
              uv cache : /home/alice/.cache/uv (persistent)

  Python 3.11.15 (Active) | Run 'py38' (up to 'py313') to switch

  Run 'tips' to explore more high-efficiency commands

mindstudio@alice-build-env:/home/alice$
```

After you enter the container, you can perform development work such as compilation and unit testing by referring to the corresponding guides.

## 6. Host Machine: Re-entering the Container

After you exit the container or restart the host machine, you can re-enter the created build container in the following ways.

### 6.1 Method 1: Entering by Menu Selection (Recommended)

Run the startup script again. The script automatically matches the container created by the current user. The container name contains the name of the currently logged-in user:

```bash
~/ctr_in.py
```

If multiple containers are matched, enter the corresponding number as prompted. If only one is matched, the script enters it automatically.

### 6.2 Method 2: Entering by Specifying the Container Name

```bash
~/ctr_in.py <CONTAINER_NAME>
```

## 7. FAQ

### 7.1 What Should I Do If a Permission Denied Error Occurs When Running Docker Commands?

The current user may not be a member of the Docker user group. Run the following command on the host machine with root privileges:

```bash
sudo usermod -aG docker <username>
```

After running the command, log in again to the current user session, or run `newgrp docker` to make the user group change take effect immediately. You are advised not to perform routine operations as root.

### 7.2 What Should I Do If Image Pulling Fails?

Troubleshoot in the following order:

1. Run `docker info` to confirm that the Docker service is normal.
2. Check whether the current network can access `swr.cn-north-4.myhuaweicloud.com`.
3. If you are on a corporate intranet, configure a Docker proxy according to the actual network policies.
4. Run `docker system df` to confirm that the Docker data directory has sufficient space.

### 7.3 What Should I Do If Downloading `ctr_in.py` Fails?

If the `curl` download fails, manually copy the `ctr_in.py` script to the `~/` directory on the host machine, and then grant it execute permissions:

```bash
cd ~
chmod +x ctr_in.py
ls -l ctr_in.py
```

### 7.4 What If the MindStudio Welcome Screen Does Not Appear After Startup?

First, confirm whether you have entered the container. If you are still on the host machine, run the startup command in [Section 5](#5-host-machine-starting-and-entering-the-build-container) again. If the container has started but you have not entered it, re-enter it as described in [Section 6](#6-host-machine-re-entering-the-container).
