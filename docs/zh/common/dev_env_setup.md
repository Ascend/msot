# 算子工具开发环境安装指导

<br>

## 前置条件

请确保以下依赖已正确安装并运行：

| 依赖项               | 说明 | 验证命令 |
|-------------------| --- | --- |
| **Docker Engine** | 已安装且服务正在运行 | `docker info` |
| **Python3**       | 宿主机已安装（任意 3.x 版本） | `python3 -V` |

---

## 1. 拉取编译专用镜像

从华为云官方容器镜像仓库拉取定制的开发镜像：

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-20260610
```

> [!NOTE] 编译镜像说明   
> 
> * **操作系统**：openEuler 22.03 LTS。
> * **C++ 工具链**：GCC 11.2，兼容 glibc ≥ 2.17。
> * **Python 环境**：原生支持 3.8–3.13（符合 manylinux2014 标准）。
> * **CANN 运行环境**：预装 CANN 9.1.0-beta.1，已深度裁剪非编译组件以优化体积。

## 2. 启动开发容器

### 2.1 获取启动脚本

```shell
cd ~ && curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

### 2.2 启动容器

```shell
~/ctr_in.py swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-20260610
```

**预期输出：**  
终端显示类似如下提示，进入交互式 shell 即表示环境启动成功：

```text
=================================================================
           >>>>>   MindStudio Build Environment   <<<<<
    THE END-TO-END TOOLCHAIN TO UNLEASH HUAWEI ASCEND COMPUTE
=================================================================
  OS/Arch   : openEuler 22.03 (LTS-SP4) | x86_64
  Toolchain : GCC 11.2.0 | glibc <= 2.17 | CANN 9.1.0
              ccache   : /home/alice/.cache/ccache (persistent)
              uv cache : /home/alice/.cache/uv (persistent)

  Python 3.11.15 (Active) | Run 'py38' (up to 'py313') to switch

  Run 'tips' to explore more high-efficiency commands

mindstudio@alice-build-env:/home/alice$
```

> [!NOTE] 说明
> **退出容器后如何重新进入？**
>
> 1. 快捷方式：`~/ctr_in.py`，交互式选择进入当前用户创建的容器，结果唯一则直接进入。
> 2. 原生命令：`docker exec -it alice_YYMMD_HHMMSS bash`（替换为实际容器名）。
