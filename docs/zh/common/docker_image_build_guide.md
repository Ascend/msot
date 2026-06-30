# MindStudio 统一构建镜像制作指南

<br>

本文档介绍如何基于 openEuler 操作系统，构建集成了 GCC、Python 及昇腾 CANN 软件包的 MindStudio 编译镜像。

## 1. 镜像组成说明

为了提高日常更新和分发的效率，镜像采用分层构建模式。自底向上依次叠加，以便在软件更新时深度复用底层缓存，加速构建过程：

| 镜像层级 | 核心组件 | 说明                                      |
| :--- | :--- |:----------------------------------------|
| **顶层 (Layer 4)** | 昇腾 CANN 软件包 | 业务最常更新的部分（包含 CANN 运行与开发环境）              |
| **第三层 (Layer 3)** | Python 环境 | 基于 PyPA 标准安装的 Python 环境（与 GCC 共同构成基础构建镜像） |
| **第二层 (Layer 2)** | GCC 11 | 核心编译工具链                                 |
| **底层 (Layer 1)** | openEuler 基础系统 | 操作系统底座，提供基础系统库                          |

> [!NOTE] 主要软件环境说明   
> 
> * **操作系统**：openEuler 24.03 LTS。
> * **C++ 工具链**：GCC 11.2，兼容 glibc ≥ 2.17。
> * **Python 环境**：原生支持 3.8–3.13（符合 manylinux2014 标准）。
> * **CANN 运行环境**：预装 CANN 配套版本，已深度裁剪非编译组件以优化体积。

## 2. 环境准备：安装 Docker 服务

> ⚠️ **前置要求**：Docker 版本须 **> 23**（本示例统一安装 `26.1.3` 版本）。

若宿主机尚未安装 Docker，可参考以下在 **openEuler 22.03** 宿主机上的安装命令，若在其它 Linux 发行版环境遇异常，请结合实际情况调整。

```bash
# 1. 配置 Docker CE 仓库
sudo wget -O /etc/yum.repos.d/docker-ce.repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's/$releasever/8/g' /etc/yum.repos.d/docker-ce.repo

# 2. 安装 Docker 核心组件及 Git
sudo dnf install -y docker-ce-26.1.3 docker-ce-cli-26.1.3 containerd.io docker-buildx-plugin docker-compose-plugin git --disablerepo=debuginfo,source,update-source,EPOL

# 3. 启动 Docker 服务并设置开机自启
sudo systemctl enable --now docker
```

## 3. 镜像构建步骤

### 3.1 下载构建脚本

获取官方提供的 Dockerfile 及相关构建辅助脚本：

```bash
cd ~
curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/env/build/source/master/dockerfile.tar.gz
tar zxvf dockerfile.tar.gz
cd docker
```

### 3.2 设置镜像标签 (TAG)

运行以下命令，系统会根据当前机器的硬件架构（ARM64 / AMD64）自动追加后缀并设置环境变量：

```bash
export IMG_TAG="1.0.0-$([ "$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")"
```

### 3.3 执行镜像构建

执行 Python 脚本开始构建，**整个构建过程大约需要 30 分钟**：

```bash
python3 build_image.py -t ${IMG_TAG} --force \
-c https://ascend-cann-open.obs.cn-north-4.myhuaweicloud.com/CANN/CANN%209.1.0-beta.3/Ascend-cann_9.1.0-beta.3_linux-$(arch).run \
-c https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN%209.1.T6/Ascend-cann-910b-ops_9.1.0-beta.3_linux-$(arch).run
```

构建完成后，执行以下命令确认镜像已生成（标签为上一步设置的 `${IMG_TAG}`）：

```bash
docker images | grep ${IMG_TAG}
```
