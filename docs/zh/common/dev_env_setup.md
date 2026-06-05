# 算子工具开发环境安装指导

<br>

## 1. 拉取编译专用镜像

请从华为云官方容器镜像仓库拉取 Docker 镜像：

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-20260530
```

> [!NOTE] 编译镜像说明   
> **操作系统**：本镜像基于 openEuler 22.03 构建。  
> **C++ 环境**：采用 GCC 11.2 编译器，基于 GLIBC 2.17 运行时编译，确保编译产物完全兼容 GLIBC 2.17 及以上版本。   
> **Python 环境**：遵循 PyPA manylinux2014 标准构建，原生支持 3.8 ~ 3.13 版本。   
> **CANN 环境**：集成 CANN 9.1.0-beta.1 版本，已深度裁剪非编译相关组件以优化镜像体积。

## 2. 启动容器

### 2.1 下载容器启动脚本

执行如下命令下载：

```shell
cd ~
curl -fLO --retry 10 --retry-all-errors --retry-delay 3 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" https://raw.gitcode.com/Ascend/msot/raw/master/example/quick_start/public/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE] 说明
> 1.若提示 `--retry-all-errors` 参数不存在，说明 curl 版本过低，可移除该参数后重试。  
> 2.若多次下载仍失败，可能是触发了防止自动化脚本恶意爬取代码的 CDN 防护机制，可手动从仓库下载 [ctr_in.py](../../../example/quick_start/public/ctr_in.py) 文件。

### 2.2 执行启动命令

**参数说明：**

| 参数               | 说明                                   | 示例              |
| ---------------- | ------------------------------------ | --------------- |
| `CONTAINER_NAME` | 容器名称，后续可通过该名称登录容器，建议格式：`{用途}_{个人标识}` | `op_dev_alice` |
| `USER_NAME`      | 宿主机用户名，用于挂载 `$HOME` 目录实现数据共享         | `alice`         |
| `IMAGE`          | Docker 镜像 ID 或完整名称                   | `6df0c5bbc16f`  |

**命令格式：**

```shell
python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>
```

**执行示例：**

```shell
# 使用镜像 ID
python3 ~/ctr_in.py op_dev_alice alice 6df0c5bbc16f

# 使用镜像全名
python3 ~/ctr_in.py op_dev_alice alice swr.cn-north-4.myhuaweicloud.com/mindstudio-image/mindstudio-build:26.1.0-20260530
```

**预期输出：**    
启动成功后将直接进入容器，终端显示容器内的命令行提示符，等待输入命令：

```text
Welcome to 5.10.0-60.139.0.166.oe2203.aarch64

System information as of time:  Fri Mar 20 06:46:56 UTC 2026
System load:    8.95
Memory used:    6.2%
Swap used:      55.4%
Usage On:       25%
Users online:   0

[root@localhost alice]#
```

> [!NOTE] 说明
> **退出后如何重新进入容器？**
>
> 1. 执行：`python3 ~/ctr_in.py op_dev_alice`，当仅传入 1 个参数时，该脚本将执行进入已有容器的操作，且支持模糊匹配容器名。
> 2. 也可使用 Docker 原生命令：`docker exec -it op_dev_alice bash`。

## 3. 环境设置

进入容器后，CANN 相关环境变量及基于 GLIBC 2.17 的 GCC 11.2 编译环境均已自动配置，无需手动设置。

**切换 Python 版本**

容器默认使用操作系统自带的 Python。如构建Python工程，需启用符合 PyPA manylinux2014 标准的 Python 环境，请执行以下命令切换至所需版本（支持 3.8 ~ 3.13）：
```shell
# 以切换至 Python 3.11 版本为例
source use-python 3.11

# 验证版本
python3 --version
```


