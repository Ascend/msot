# MindStudio Unified Build Image Creation Guide

<br>

This document describes how to build the MindStudio compilation image based on the openEuler operating system, with GCC, Python, and Ascend CANN software packages integrated.

This document is intended only for developers who need to **customize the image content or reproduce the image build process**. If you only need to set up a routine development environment, first refer to the [MindStudio Tool Development Environment Setup Guide](./dev_env_setup.md).

## 1. Applicable Scenarios and Image Composition

To improve the efficiency of routine updates and distribution, the image uses a layered build model. Layers are stacked from the bottom up so that the lower-layer cache is fully reused when software is updated, accelerating the build process:

| Image Layer | Core Components | Description |
| :--- | :--- | :--- |
| **Top layer (Layer 4)** | Ascend CANN software packages | The part most frequently updated by the service, including the CANN runtime and development environment |
| **Third layer (Layer 3)** | Python environment and related toolchain | Python environment installed per the PyPA standard, forming the base build image together with GCC |
| **Second layer (Layer 2)** | GCC 11 and related toolchain | Core compilation toolchain |
| **Bottom layer (Layer 1)** | openEuler base system | Operating system foundation that provides the basic system libraries |

> [!NOTE]Note
>
> **Primary Software Environment**
>
> - **OS**: openEuler 24.03 LTS
> - **C++ toolchain**: GCC 11.2, compatible with glibc ≥ 2.17
> - **Python environment**: native support for 3.8–3.13, compliant with the manylinux2014 standard
> - **CANN runtime environment**: The matching CANN version is pre-installed, with non-compilation components trimmed to optimize the image size.

## 2. Prerequisites

Ensure that the host meets the following requirements:

| Dependency | Requirement | Verification Command |
| --- | --- | --- |
| **Docker Engine** | Version 23.0 or later, and the Docker service is running properly | `docker info` returns information without errors. |
| **Docker Buildx** | Installed and runnable | `docker buildx version` outputs version information. |
| **Python 3** | Installed (any 3.x version) | `python3 -V` outputs version information. |
| **curl** | Installed (any version) | `curl -V` outputs version information. |
| **Drive space** | The Docker data directory must have enough space to store the build context, base images, and build cache | `df -h $(docker info -f '{{.DockerRootDir}}')` shows that Avail is at least 20 GB. |
| **Network access** | Direct Internet access to the script download URL, CANN run package URLs, and so on | `curl -I https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py` returns `200 OK`. |

If `docker info` reports a permission denied error, first resolve the Docker permission issue as described in [Section 8.1](#81-what-to-do-when-docker-commands-report-a-permission-denied-error).

## 3. Host: Installing and Verifying Docker

If Docker is not installed on the host, run the following commands to install Docker on an **openEuler** host.

> [!CAUTION]Caution
>
> The following commands apply only to openEuler environments. If you use another Linux distribution, adjust the commands according to the distribution differences, or refer to the official Docker installation method.

```bash
# 1. Configure the Docker CE repository
sudo curl -fL -o /etc/yum.repos.d/docker-ce.repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's/$releasever/8/g' /etc/yum.repos.d/docker-ce.repo

# 2. Install Docker core components and Git
sudo dnf install -y docker-ce-26.1.3 docker-ce-cli-26.1.3 containerd.io docker-buildx-plugin docker-compose-plugin git --disablerepo=debuginfo,source,update-source,EPOL

# 3. Start the Docker service and enable it on startup
sudo systemctl enable --now docker
```

After the installation, run the following commands to verify that Docker and Buildx are available:

```bash
docker --version
docker buildx version
```

## 4. Host: Downloading the Build Scripts

Download the official Dockerfile and the related build helper scripts:

```bash
cd ~
curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/build/source/master/dockerfile.tar.gz
tar zxvf dockerfile.tar.gz
cd docker
```

> [!CAUTION]Caution
>
> The `-v` parameter of the `tar zxvf` extraction command outputs the file list to stdout. **Never** combine the extraction command with a truncating pipe such as `| head` or `| tail` (for example, `tar zxvf xxx.tar.gz | head -20`). After `head` reads the specified number of lines, it closes the pipe. The tar process then receives the SIGPIPE signal and is terminated. Therefore, only some files are extracted and no error message is displayed.
>
> Correct practice:
>
> - Use `tar zxf` for extraction (without `-v`, no stdout output, and unaffected by pipes).
> - Use `tar ztf xxx.tar.gz | head -20` to view the file list (`-t` only lists files without extracting. Therefore, truncation has no side effects.)

## 5. Host: Setting the Image Tag

Run the following commands. The system automatically appends the suffix based on the hardware architecture (ARM64/AMD64) of the current machine and sets the environment variable:

```bash
export IMG_TAG="1.0.0-$([ "$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")"
echo "IMG_TAG=${IMG_TAG}"
```

## 6. Host: Running the Image Build

Run the Python script to start the build. The entire build process usually takes about 20 minutes. The actual duration depends on the network speed, drive performance, and Docker cache hits:

```bash
python3 build_image.py -t ${IMG_TAG} --force \
-c https://ascend-cann-open.obs.cn-north-4.myhuaweicloud.com/CANN/CANN%209.1.0/Ascend-cann_9.1.0_linux-$(arch).run  \
-c https://ascend-cann-open.obs.cn-north-4.myhuaweicloud.com/CANN/CANN%209.1.0/Ascend-cann-910b-ops_9.1.0_linux-$(arch).run
```

Parameters:

| Parameter | Description |
| --- | --- |
| `-t ${IMG_TAG}` | Specifies the tag of the built image. |
| `--force` | Forces a rebuild, avoiding the reuse of intermediate states that do not meet expectations. |
| `-c <URL>` | Specifies the download URL of the CANN run package. Pass two CANN packages: `toolkit` and `ops`. |

> [!CAUTION]Caution
>
> The preceding command is the default environment build baseline for source compilation and unit tests of current MindStudio tools. When the documentation of a service repository does not explicitly specify another version, you must use the preceding toolkit and ops software package URLs as is, and ensure that all CANN software packages use the same version.
>
> To upgrade the unified build environment, modify only the default command and the supporting software versions in this guide. Service repositories do not need to maintain version information separately.

## 7. Host: Verifying and Starting the Image

After the build completes, run the following command to confirm that the image has been generated:

```bash
docker images | grep "${IMG_TAG}"
```

Download the container startup script:

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

Run the following command to start and enter the container in a session with an interactive terminal (TTY). Because the most recently built image appears at the top of the `docker images` output, the script automatically selects the first result that matches the tag as the image to start:

```bash
~/ctr_in.py "$(docker images --format '{{.Repository}}:{{.Tag}}' | grep "${IMG_TAG}" | head -n1)"
```

> [!CAUTION]Caution
>
> You must use the preceding `ctr_in.py` command to create and enter the container. Do not replace it with a plain `docker run`. `ctr_in.py` preserves the image entrypoint script, maps users, mounts directories, initializes the environment, and enters an interactive shell.
>
> The source compilation and unit test commands for subsequent service repositories must run in the same interactive shell opened by `ctr_in.py`. Do not exit it and then switch to `docker exec <container_name> bash -c '<command>'`. A non-interactive shell does not fully run the initialization scripts in `/etc/profile.d/`, which may prevent the Python version, GCC, or CANN environment from being activated correctly.
>
> When an automated tool runs this section, it must allocate a TTY and keep reusing that interactive session. If the session is interrupted unexpectedly, use `~/ctr_in.py <container_name>` to enter the container interactively again before you continue.

## 8. FAQ

### 8.1 What to Do When Docker Commands Report a Permission Denied Error?

The current user may not be a member of the Docker user group. Run the following command with root privileges on the host:

```bash
sudo usermod -aG docker <username>
```

After running the command, log in to the current user session again, or run `newgrp docker` to make the user group change take effect immediately. You are advised not to perform routine operations as root.

### 8.2 What to Do When You Cannot Access Internet Resources from an Intranet?

During execution, this build script frequently accesses external networks to download required dependencies. It **does not support builds in pure intranet environments**. If your host cannot connect to the Internet, move it to a network environment with direct public Internet access and try again.

### 8.3 What to Do When the Build Reports Insufficient Drive Space?

First, run the following command to check Docker space usage:

```bash
docker system df
```

After confirming that no service images depend on them, clean up unused build caches and dangling images as needed:

```bash
docker builder prune
docker image prune
```
