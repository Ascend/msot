# MindStudio Unified Build Image Creation Guide

<br>

This document describes how to build the MindStudio compilation image based on the openEuler operating system, with GCC, Python, and Ascend CANN software packages integrated.

This document is intended only for developers who need to **customize the image content or reproduce the image build process**. If you only need to set up a routine development environment, first refer to the [MindStudio Tool Development Environment Installation Guide](./dev_env_setup.md) to pull the published image directly.

## 1. Applicable Scenarios and Image Composition

To improve the efficiency of routine updates and distribution, the image uses a layered build model. Layers are stacked from the bottom up so that the lower-layer cache is fully reused when software is updated, accelerating the build process:

| Image Layer | Core Components | Description |
| :--- | :--- | :--- |
| **Top layer (Layer 4)** | Ascend CANN software packages | The part most frequently updated by the service, including the CANN runtime and development environment |
| **Third layer (Layer 3)** | Python environment | Python environment installed per the PyPA standard, forming the base build image together with GCC |
| **Second layer (Layer 2)** | GCC 11 | Core compilation toolchain |
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
| **Docker engine** | Version 23 or later is recommended. This example uses 26.1.3 | `docker info` returns information without errors. |
| **Docker Buildx** | Installed and runnable | `docker buildx version` outputs version information. |
| **Python 3** | Any 3.x version installed | `python3 -V` outputs version information. |
| **curl** | Used to download build scripts | `curl -V` outputs version information. |
| **Drive space** | The Docker data directory must have enough space to store the build context, base images, and build cache | `df -h $(docker info -f '{{.DockerRootDir}}')` shows that Avail is greater than 20 GB. |
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

## 5. Host: Setting the Image Tag

Run the following commands. The system automatically appends the suffix based on the hardware architecture (ARM64/AMD64) of the current machine and sets the environment variable:

```bash
export IMG_TAG="1.0.0-$([ "$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")"
echo "IMG_TAG=${IMG_TAG}"
```

## 6. Host: Running the Image Build

Run the Python script to start the build. The entire build process usually takes about 30 minutes. The actual duration depends on the network speed, drive performance, and Docker cache hits:

```bash
python3 build_image.py -t ${IMG_TAG} --force \
-c https://ascend-cann-open.obs.cn-north-4.myhuaweicloud.com/CANN/CANN%209.1.0-beta.3/Ascend-cann_9.1.0-beta.3_linux-$(arch).run \
-c https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN%209.1.T6/Ascend-cann-910b-ops_9.1.0-beta.3_linux-$(arch).run
```

Parameters:

| Parameter | Description |
| --- | --- |
| -t ${IMG_TAG} | Specifies the tag of the built image. |
| --force | Forces a rebuild, avoiding the reuse of intermediate states that do not meet expectations. |
| -c <URL> | Specifies the download URL of the CANN run package. Pass two CANN packages: `toolkit` and `ops` |

> [!CAUTION]Caution
>
> The CANN run package URLs in the preceding command are only examples. To build an image with another CANN version, replace them with the run package URLs of the corresponding version and ensure that the CANN package versions are consistent.

## 7. Host: Verifying and Starting the Image

After the build completes, run the following command to confirm that the image has been generated:

```bash
docker images | grep "${IMG_TAG}"
```

Download the container startup script:

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

Start the container. Because the most recently built image appears at the top of the `docker images` output, the script automatically selects the first result that matches the tag as the image to start:

```bash
~/ctr_in.py "$(docker images --format '{{.Repository}}:{{.Tag}}' | grep "${IMG_TAG}" | head -n1)"
```

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
