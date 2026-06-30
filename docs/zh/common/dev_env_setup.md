# MindStudio 工具开发环境安装指导

<br>

## 前置条件

请确保以下依赖已正确安装并运行：

| 依赖项               | 说明 | 验证命令 |
|-------------------| --- | --- |
| **Docker Engine** | 已安装且服务正在运行 | `docker info` |
| **Python3**       | 宿主机已安装（任意 3.x 版本） | `python3 -V` |

---

## 1. 获取开发专用镜像

从华为云 SWR 镜像仓库拉取定制好的 MindStudio 编译专用镜像：

```bash
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-0701
```

> [!NOTE] 如何自行构建该镜像？   
> 
> 该开发镜像内部组件较为复杂。如需了解其分层架构或需要从头构建此镜像，请参考文档：《[MindStudio 统一构建镜像制作指南](./docker_image_build_guide.md)》

## 2. 部署并启动开发容器

### 2.1 下载并配置启动脚本

获取用于自动化创建和配置容器的辅助脚本，并赋予执行权限：

```bash
cd ~ && curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

### 2.2 初始化并进入容器

运行脚本并指定刚刚拉取的镜像名称。脚本会自动处理目录挂载、用户映射及环境变量初始化：

```bash
~/ctr_in.py swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-0701
```

#### 预期输出

命令执行后，终端将自动切换至容器内的交互式 Shell，并显示如下 MindStudio 欢迎界面，即表示环境搭建成功：

```text
=================================================================
           >>>>>   MindStudio Build Environment   <<<<<
    THE END-TO-END TOOLCHAIN TO UNLEASH HUAWEI ASCEND COMPUTE
=================================================================
  OS/Arch   : openEuler 24.03 (LTS-SP3) | x86_64
  Toolchain : GCC 11.2.0 | glibc <= 2.17 | CANN 9.1.0
              ccache   : /home/alice/.cache/ccache (persistent)
              uv cache : /home/alice/.cache/uv (persistent)

  Python 3.11.15 (Active) | Run 'py38' (up to 'py313') to switch

  Run 'tips' to explore more high-efficiency commands

mindstudio@alice-build-env:/home/alice$
```

## 3. 日常运维：重新进入容器

当您退出容器或重启宿主机后，可以通过以下两种方式重新进入已创建的开发环境：

### 方法一：通过脚本快捷进入（推荐）

再次执行启动脚本，脚本会智能识别当前用户创建的容器：

```bash
~/ctr_in.py
```

若存在多个容器，请根据终端的交互式提示输入对应编号；若结果唯一，则会自动直接进入。

### 方法二：使用原生 Docker 命令

如果您希望跳过脚本，可以直接使用 Docker 原生命令进入（请将 `<CONTAINER_NAME>` 替换为实际的容器名，如 `alice_20260606_120000`）：

```bash
docker exec -it <CONTAINER_NAME> bash
```
