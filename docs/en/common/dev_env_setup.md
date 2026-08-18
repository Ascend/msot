# MindStudio Tool Development Environment Setup Guide

<br>

This document describes how to set up a standardized container environment for MindStudio tool development tasks such as compilation and unit testing (UT). Unless otherwise specified, all commands in this document are run on the **host machine**.

## 1. Prerequisites

Ensure that the following dependencies are installed and running properly:

| Dependency | Description | Verification Command |
| --- | --- | --- |
| **Docker Engine** | Installed and the service is running | Run `docker ps`. If no error is reported, the service started properly. |
| **Python 3** | Installed on the host machine (any 3.x version) | Run `python3 -V`. Version information in the output indicates that Python is installed. |

---

If a permission denied error occurs when you run `docker ps`, refer to [Section 6.1](#61-what-should-i-do-if-a-permission-denied-error-occurs-when-running-docker-commands) to handle Docker permissions first.

## 2. Host Machine: Pulling the Dedicated Development Image

Pull the customized MindStudio build image from the Huawei Cloud SWR image repository:

```bash
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-0701
```

If image pulling fails, first check the network proxy or the space in the Docker data directory.

> [!NOTE] How do I build the image myself?
>
> You usually do not need to build the image yourself. Only when you need to customize the image content, troubleshoot image layers, or reproduce the build process, refer to the [MindStudio Unified Build Image Guide](./docker_image_build_guide.md).

## 3. Host Machine: Downloading the Container Startup Script

Download the helper script for automatically creating and configuring containers, and grant it execute permissions:

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE] Note
>
> The `ctr_in.py` script is powerful and can serve as a general-purpose tool for routine container operations. View its specific functions and usage with the `--help` parameter.

## 4. Host Machine: Starting and Entering the Development Container

Run the script and specify the name of the image you just pulled. The script automatically handles directory mounting, user mapping, and environment variable initialization:

```bash
~/ctr_in.py swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-0701
```

### Expected Output

After the command runs, the terminal automatically switches to the interactive shell in the container and displays the following MindStudio welcome screen, indicating that the container has started and you have entered it successfully:

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

## 5. Host Machine: Re-entering the Container

After you exit the container or restart the host machine, you can re-enter the created development environment in either of the following two ways. All commands in this chapter are run on the **host machine**.

### 5.1 Method 1: Entering Quickly Using the Script (Recommended)

Run the startup script again. The script intelligently identifies the container created by the current user:

```bash
~/ctr_in.py
```

If multiple containers exist, enter the corresponding number as prompted in the terminal. If only one container is found, the script enters it directly.

### 5.2 Method 2: Using Native Docker Commands

First, query the container name:

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
```

Then use the native Docker command to enter the container. Replace `<CONTAINER_NAME>` with the actual container name, for example, `alice_20260606_120000`:

```bash
docker exec -it <CONTAINER_NAME> bash
```

## 6. FAQ

### 6.1 What Should I Do If a Permission Denied Error Occurs When Running Docker Commands?

The current user may not be a member of the Docker user group. Run the following command on the host machine with root privileges:

```bash
sudo usermod -aG docker <username>
```

After running the command, log in again to the current user session, or run `newgrp docker` to make the user group change take effect immediately. You are advised not to perform routine operations as root.

### 6.2 What Should I Do If Image Pulling Fails?

Troubleshoot in the following order:

1. Run `docker info` to confirm that the Docker service is normal.
2. Check whether the current network can access `swr.cn-north-4.myhuaweicloud.com`.
3. If you are on a corporate intranet, configure a Docker proxy according to the actual network policies.
4. Run `docker system df` to confirm that the Docker data directory has sufficient space.

### 6.3 What Should I Do If Downloading `ctr_in.py` Fails?

Use the manual download method in [Section 3](#3-host-machine-downloading-the-container-startup-script), copy the script to the `~/` directory on the host machine, and then run:

```bash
cd ~
chmod +x ctr_in.py
ls -l ctr_in.py
```

### 6.4 What If the MindStudio Welcome Screen Does Not Appear After Startup?

First, confirm whether you have entered the container. If you are still on the host machine, run the startup command in [Section 4](#4-host-machine-starting-and-entering-the-development-container) again. If the container has started but you have not entered it, re-enter it as described in [Section 5](#5-host-machine-re-entering-the-container).
