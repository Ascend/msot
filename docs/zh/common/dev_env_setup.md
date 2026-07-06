# MindStudio 工具开发环境安装指导

<br>

本文档用于搭建 MindStudio 工具编译/UT 等开发所需的标准化容器环境。除特别说明外，本文命令均在**宿主机**执行。

## 1. 前置条件

请确保以下依赖已正确安装并运行：

| 依赖项               | 说明 | 验证命令 |
|-------------------| --- | --- |
| **Docker Engine** | 已安装且服务正在运行 | 执行 `docker ps`，无报错即表示服务正常启动 |
| **Python 3**       | 宿主机已安装（任意 3.x 版本） | 执行 `python3 -V`，有版本信息输出即表示已安装 |

---

若 `docker ps` 出现 permission denied 类错误，请先参考 [6.1 节](#61-执行-docker-命令遇到-permission-denied-类错误提示) 处理 Docker 权限。

## 2. 宿主机：拉取开发专用镜像

从华为云 SWR 镜像仓库拉取定制好的 MindStudio 编译专用镜像：

```bash
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-0701
```

若镜像拉取失败，请优先检查网络代理或 Docker 数据目录空间。

> [!NOTE] 如何自行构建该镜像？
>
> 普通开发者通常无需自行构建镜像。仅当需要定制镜像内容、排查镜像分层或复现构建过程时，请参考文档：《[MindStudio 统一构建镜像制作指南](./docker_image_build_guide.md)》。

## 3. 宿主机：下载容器启动脚本

获取用于自动化创建和配置容器的辅助脚本，并赋予执行权限：

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE]说明
>
> 此 `ctr_in.py` 脚本功能强大，可作为日常容器操作的通用工具。具体功能及用法可通过 `--help` 参数查看。

## 4. 宿主机：启动并进入开发容器

运行脚本并指定刚刚拉取的镜像名称。脚本会自动处理目录挂载、用户映射及环境变量初始化：

```bash
~/ctr_in.py swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-0701
```

### 预期输出

命令执行后，终端将自动切换至容器内的交互式 Shell，并显示如下 MindStudio 欢迎界面，即表示容器已启动并成功进入：

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

## 5. 宿主机：重新进入容器

当您退出容器或重启宿主机后，可以通过以下两种方式重新进入已创建的开发环境。本章命令均在**宿主机**执行。

### 5.1 方法一：通过脚本快捷进入（推荐）

再次执行启动脚本，脚本会智能识别当前用户创建的容器：

```bash
~/ctr_in.py
```

若存在多个容器，请根据终端的交互式提示输入对应编号；若结果唯一，则会自动直接进入。

### 5.2 方法二：使用原生 Docker 命令

先查询容器名称：

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
```

然后使用 Docker 原生命令进入容器，请将 `<CONTAINER_NAME>` 替换为实际容器名，如 `alice_20260606_120000`：

```bash
docker exec -it <CONTAINER_NAME> bash
```

## 6. FAQ

### 6.1 执行 Docker 命令遇到 permission denied 类错误提示？

可能当前用户未加入 Docker 用户组。可使用 root 权限在宿主机执行：

```bash
sudo usermod -aG docker <当前用户名>
```

执行后需要重新登录当前用户会话，或执行 `newgrp docker` 使用户组变更立即生效。不建议以 root 身份进行日常操作。

### 6.2 拉取镜像失败如何处理？

请按以下顺序排查：

1. 执行 `docker info`，确认 Docker 服务正常。
2. 检查当前网络是否可访问 `swr.cn-north-4.myhuaweicloud.com`。
3. 若处于企业内网，请根据实际网络策略配置 Docker 代理。
4. 执行 `docker system df`，确认 Docker 数据目录空间充足。

### 6.3 下载 `ctr_in.py` 失败如何处理？

优先使用 [第 3 章](#3-宿主机下载容器启动脚本) 中的手动下载方式，将脚本拷贝至宿主机 `~/` 目录后执行：

```bash
cd ~
chmod +x ctr_in.py
ls -l ctr_in.py
```

### 6.4 启动后没有看到 MindStudio 欢迎界面？

请先确认是否已经进入容器。如果仍在宿主机，请重新执行 [第 4 章](#4-宿主机启动并进入开发容器) 的启动命令。若容器已启动但未进入，可按 [第 5 章](#5-宿主机重新进入容器) 重新进入。
