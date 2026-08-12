# MindStudio 工具开发环境安装指导

<br>

本文档用于搭建 MindStudio 工具编译/UT 等开发所需的标准化容器环境。

## 1. 方式选择

MindStudio 工具支持两种开发环境安装方式，请根据仓库实际情况选择：

| 方式 | 适用条件                       | 说明 |
| --- |----------------------------| --- |
| **Dev Containers** | 仓库根目录包含 `.devcontainer` 目录 | 开箱即用，具体步骤详见仓库内 `.devcontainer` 目录下的 README 说明 |
| **命令行容器环境（通用方式）** | 所有 Linux 命令行工具的仓库          | 即本文后续章节介绍的方式 |

> [!NOTE]说明
>
> 若仓库已配置 `.devcontainer` 目录，建议优先选用 Dev Containers 方式，效率最高；否则请按本文后续章节搭建命令行容器环境。

## 2. 前置条件

请确保以下依赖已正确安装并运行：

| 依赖项               | 说明 | 验证命令 |
|-------------------| --- | --- |
| **Docker Engine** | 已安装且服务正在运行 | 执行 `docker ps`，无报错即表示服务正常启动 |
| **Python 3**       | 宿主机已安装（任意 3.x 版本） | 执行 `python3 -V`，有版本信息输出即表示已安装 |

---

若 `docker ps` 出现 permission denied 类错误，请先参考 [7.1 节](#71-执行-docker-命令遇到-permission-denied-类错误提示) 处理 Docker 权限。

## 3. 宿主机：拉取编译专用镜像

从华为云 SWR 镜像仓库拉取定制好的 MindStudio 编译专用镜像：

```bash
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.2.0-0801
```

> [!NOTE]说明
>
> **如何自行构建该镜像？**
>
> 普通开发者通常无需关注此步骤。仅当需要定制镜像内容、排查镜像分层或复现构建过程时，请参考《[MindStudio 统一构建镜像制作指南](./docker_image_build_guide.md)》。

若镜像拉取失败，请参考 [FAQ 2](#72-拉取镜像失败如何处理)。

## 4. 宿主机：下载容器启动脚本

获取用于自动化创建和配置容器的辅助脚本，并赋予执行权限：

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE]说明
>
> 此 `ctr_in.py` 脚本功能强大，可作为日常容器操作的通用工具。具体功能及用法可通过 `--help` 参数查看。

## 5. 宿主机：启动并进入编译容器

以**普通用户**身份执行脚本，并指定已拉取的编译镜像名称。脚本将自动完成目录挂载、用户映射及环境变量初始化：

```bash
~/ctr_in.py swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.2.0-0801
```

> [!CAUTION]注意
>
> 本镜像**仅用于编译，不支持 NPU 程序运行**（原因：CANN 容器运行需 root 权限，编译产生大量 root 属主文件污染 HOME 目录；为控制镜像体积深度裁剪了运行库）。
> 
> 如需运行 NPU 程序，建议使用如下“**双终端模式**”开发方式，两端共享 HOME 目录，编译、运行与宿主机三套环境互不干扰，开发效率更高：
>
> **终端 1（编译）**：启动本编译镜像容器，编译产物输出至 HOME 目录；
>
> **终端 2（运行）**：启动 CANN 官方运行容器，从 HOME 目录读取并执行，启动命令示例如下，具体版本等信息请参考 [CANN 官方镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)：
>
> ```bash
> ~/ctr_in.py swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12
> ```

### 预期输出

命令执行后，终端将自动切换至容器内的交互式 Shell，并显示类似如下 MindStudio 欢迎界面，即表示容器已启动并成功进入：

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

进入容器后，即可参照相应指南执行编译、单元测试等开发工作。

## 6. 宿主机：重新进入容器

退出容器或重启宿主机后，可通过以下方式重新进入已创建的编译容器。

### 6.1 方法一：菜单选择式进入（推荐）

再次执行启动脚本，脚本会自动匹配当前用户创建的容器（容器名包含当前登录用户名）：

```bash
~/ctr_in.py
```

若匹配到多个容器，根据提示输入对应编号；若仅有一个，则自动进入。

### 6.2 方法二：指定容器名进入

```bash
~/ctr_in.py <容器名>
```

## 7. FAQ

### 7.1 执行 Docker 命令遇到 permission denied 类错误提示？

可能当前用户未加入 Docker 用户组。可使用 root 权限在宿主机执行：

```bash
sudo usermod -aG docker <当前用户名>
```

执行后需要重新登录当前用户会话，或执行 `newgrp docker` 使用户组变更立即生效。不建议以 root 身份进行日常操作。

### 7.2 拉取镜像失败如何处理？

请按以下顺序排查：

1. 执行 `docker info`，确认 Docker 服务正常。
2. 检查当前网络是否可访问 `swr.cn-north-4.myhuaweicloud.com`。
3. 若处于企业内网，请根据实际网络策略配置 Docker 代理。
4. 执行 `docker system df`，确认 Docker 数据目录空间充足。

### 7.3 下载 `ctr_in.py` 失败如何处理？

优先使用 [第 4 章](#4-宿主机下载容器启动脚本) 中的手动下载方式，将脚本拷贝至宿主机 `~/` 目录后执行：

```bash
cd ~
chmod +x ctr_in.py
ls -l ctr_in.py
```

### 7.4 启动后没有看到 MindStudio 欢迎界面？

请先确认是否已经进入容器。如果仍在宿主机，请重新执行 [第 5 章](#5-宿主机启动并进入编译容器) 的启动命令。若容器已启动但未进入，可按 [第 6 章](#6-宿主机重新进入容器) 重新进入。
