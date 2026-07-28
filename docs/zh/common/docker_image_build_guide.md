# MindStudio 统一构建镜像制作指南

<br>

本文档介绍如何基于 openEuler 操作系统，构建集成了 GCC、Python 及昇腾 CANN 软件包的 MindStudio 编译镜像。

本文档仅面向需要**自定义镜像内容或复现镜像构建过程**的开发者。若只是搭建日常开发环境，请优先参考《[MindStudio 工具开发环境安装指导](./dev_env_setup.md)》直接拉取已发布镜像。

## 1. 适用场景与镜像组成

为了提高日常更新和分发的效率，镜像采用分层构建模式。自底向上依次叠加，以便在软件更新时充分复用底层缓存，加速构建过程：

| 镜像层级 | 核心组件 | 说明 |
| :--- | :--- | :--- |
| **顶层（Layer 4）** | 昇腾 CANN 软件包 | 业务最常更新的部分，包含 CANN 运行与开发环境 |
| **第三层（Layer 3）** | Python 环境 | 基于 PyPA 标准安装的 Python 环境，与 GCC 共同构成基础构建镜像 |
| **第二层（Layer 2）** | GCC 11 | 核心编译工具链 |
| **底层（Layer 1）** | openEuler 基础系统 | 操作系统底座，提供基础系统库 |

> [!NOTE]说明
>
> **主要软件环境**
>
> - **操作系统**：openEuler 24.03 LTS。
> - **C++ 工具链**：GCC 11.2，兼容 glibc ≥ 2.17。
> - **Python 环境**：原生支持 3.8–3.13，符合 manylinux2014 标准。
> - **CANN 运行环境**：预装 CANN 配套版本，已裁剪非编译组件以优化体积。

## 2. 前置条件

请确保宿主机满足以下要求：

| 依赖项 | 要求                                 | 验证命令                                                                           |
| --- |------------------------------------|--------------------------------------------------------------------------------|
| **Docker Engine** | 建议 23 及以上版本；本示例使用 26.1.3           | `docker info` 正常返回信息无报错                                                        |
| **Docker Buildx** | 已安装并可执行                            | `docker buildx version` 有版本信息输出                                                |
| **Python 3** | 已安装任意 3.x 版本                       | `python3 -V` 有版本信息输出                                                            |
| **curl** | 用于下载构建脚本                           | `curl -V` 有版本信息输出                                                              |
| **磁盘空间** | Docker 数据目录需有足够空间保存构建上下文、基础镜像和构建缓存 | `df -h $(docker info -f '{{.DockerRootDir}}')` 中 Avail 大于 20 GB |
| **网络访问** | 直连互联网，可访问脚本下载地址、CANN run 包地址等      | `curl -I https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py` 返回 200 OK |

若 `docker info` 出现 permission denied 类错误，请先参考 [8.1 节](#81-执行-docker-命令遇到-permission-denied-类错误提示) 处理 Docker 权限。

## 3. 宿主机：安装并验证 Docker

若宿主机尚未安装 Docker，可参考以下命令在 **openEuler** 宿主机上安装 Docker。

> [!CAUTION]注意
>
> 以下命令仅面向 openEuler 环境。若使用其他 Linux 发行版，请根据发行版差异调整命令，或参考 Docker 官方安装方式。

```bash
# 1. 配置 Docker CE 仓库
sudo curl -fL -o /etc/yum.repos.d/docker-ce.repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's/$releasever/8/g' /etc/yum.repos.d/docker-ce.repo

# 2. 安装 Docker 核心组件及 Git
sudo dnf install -y docker-ce-26.1.3 docker-ce-cli-26.1.3 containerd.io docker-buildx-plugin docker-compose-plugin git --disablerepo=debuginfo,source,update-source,EPOL

# 3. 启动 Docker 服务并设置开机自启
sudo systemctl enable --now docker
```

安装完成后，执行以下命令验证 Docker 和 Buildx 可用：

```bash
docker --version
docker buildx version
```

## 4. 宿主机：下载构建脚本

获取官方提供的 Dockerfile 及相关构建辅助脚本：

```bash
cd ~
curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/build/source/master/dockerfile.tar.gz
tar zxvf dockerfile.tar.gz
cd docker
```

> [!CAUTION]注意
>
> 解压命令 `tar zxvf` 的 `-v` 参数会将文件列表输出到 stdout。**严禁**将解压命令与 `| head`、`| tail` 等截断管道组合使用（如 `tar zxvf xxx.tar.gz | head -20`）。`head` 读满行数后关闭管道，tar 进程收到 SIGPIPE 信号被终止，导致仅部分文件被解压且无任何错误提示。
>
> 正确做法：
> 
> - 解压用 `tar zxf`（不带 `-v`，无 stdout 输出，不受管道影响）
> - 查看文件列表用 `tar ztf xxx.tar.gz | head -20`（`-t` 只列出不解压，截断无副作用）

## 5. 宿主机：设置镜像标签

运行以下命令，系统会根据当前机器的硬件架构（ARM64 / AMD64）自动追加后缀并设置环境变量：

```bash
export IMG_TAG="1.0.0-$([ "$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64")"
echo "IMG_TAG=${IMG_TAG}"
```

## 6. 宿主机：执行镜像构建

执行 Python 脚本开始构建，整个构建过程通常需要 30 分钟左右，实际耗时取决于网络速度、磁盘性能和 Docker 缓存命中情况：

```bash
python3 build_image.py -t ${IMG_TAG} --force \
-c https://ascend-cann-open.obs.cn-north-4.myhuaweicloud.com/CANN/CANN%209.1.0-beta.3/Ascend-cann_9.1.0-beta.3_linux-$(arch).run \
-c https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN%209.1.T6/Ascend-cann-910b-ops_9.1.0-beta.3_linux-$(arch).run
```

参数说明如下：

| 参数 | 说明                                                |
| --- |---------------------------------------------------|
| `-t ${IMG_TAG}` | 指定构建出的镜像标签                                        |
| `--force` | 强制重新构建，避免复用不符合预期的中间状态                             |
| `-c <URL>` | 指定 CANN run 包下载地址，需传入 `toolkit` 和 `ops` 2 个 CANN 包 |

> [!CAUTION]注意
>
> 上述命令是当前MindStudio工具源码编译和单元测试使用的默认环境构建基线。当业务仓文档未明确指定其他版本时，必须原样使用上述toolkit和ops软件包地址，并确保多个CANN软件包版本一致。
>
> 如需升级统一构建环境，仅修改本指南中的默认命令和配套软件版本，各业务仓无需重复维护版本信息。

## 7. 宿主机：验证并启动镜像

构建完成后，执行以下命令确认镜像已生成：

```bash
docker images | grep "${IMG_TAG}"
```

下载容器启动脚本：

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

执行如下命令在具备交互式终端（TTY）的会话中启动并进入容器。由于最新构建的镜像在 `docker images` 输出中位于最上方，脚本将自动选取匹配标签的第一个结果作为启动镜像：

```bash
~/ctr_in.py "$(docker images --format '{{.Repository}}:{{.Tag}}' | grep "${IMG_TAG}" | head -n1)"
```

> [!CAUTION]注意
>
> 必须使用上述 `ctr_in.py` 命令创建并进入容器，不得替换为普通 `docker run`。`ctr_in.py` 会保留镜像入口脚本，完成用户映射、目录挂载和环境初始化，并进入交互式 Shell。
>
> 后续业务仓的源码编译和单元测试命令必须在 `ctr_in.py` 打开的同一个交互式 Shell 中执行，不得退出后改用 `docker exec <容器名> bash -c '<命令>'`。非交互式 Shell 不会完整执行 `/etc/profile.d/` 中的初始化脚本，可能导致Python版本、GCC或CANN环境未正确激活。
>
> 自动化工具执行本节时必须分配TTY，并持续复用该交互式会话。会话意外中断时，使用 `~/ctr_in.py <容器名>` 重新交互式进入容器后再继续。

## 8. FAQ

### 8.1 执行 docker 命令遇到 permission denied 类错误提示？

可能当前用户未加入 Docker 用户组。可使用 root 权限在宿主机执行：

```bash
sudo usermod -aG docker <当前用户名>
```

执行后需要重新登录当前用户会话，或执行 `newgrp docker` 使用户组变更立即生效。不建议以 root 身份进行日常操作。

### 8.2 因处在内网无法访问互联网资源？

本构建脚本在执行过程中需频繁访问外部网络以下载相关依赖，**不支持纯内网环境下的构建操作**。若您的宿主机无法连接互联网，请迁移至具备直连公网能力的网络环境后重试。

### 8.3 构建过程中提示磁盘空间不足如何处理？

先执行以下命令查看 Docker 空间占用：

```bash
docker system df
```

确认无业务镜像依赖后，可按需清理无用构建缓存和悬空镜像：

```bash
docker builder prune
docker image prune
```
