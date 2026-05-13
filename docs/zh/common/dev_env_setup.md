# 算子工具开发环境安装指导

<br>

## 1. 拉取镜像

> [!NOTE] 关于编译环境的说明
> 由于 glibc 遵循“向后兼容”但不“向前兼容”的原则，为确保编译生成的可执行程序能在大多数操作系统上运行，编译镜像通常选用较旧版本的操作系统。
> 若在较高版本操作系统上编译的程序发布到较低版本环境中运行，可能出现异常。场景二的编译专用镜像发布于 2018 年左右，可广泛适配当前主流的老旧运行环境。
> 但该操作系统版本功能较为受限（例如不支持 VS Code 远程连接），因此仅建议用于最终编译打包；日常开发与调试请使用较新镜像，以提升效率与体验。

### 场景选择指南

对于只需在单一且无须考虑跨操作系统版本兼容性的环境中进行编译和运行的情况，推荐采用**场景一**，以实现最高开发效率。
反之，如果需要将编译后的软件包部署到旧版操作系统，则应选择**场景二**。（建议首先使用场景一中的镜像完成软件的调试工作，确保其稳定性后再切换至场景二的镜像进行最终编译，以此达到开发效率与运行兼容性的平衡。）

### 场景一：单一环境下的开发与调试

请使用 CANN 官方容器镜像作为编译环境，镜像详情可参见<a href="https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884" target="_blank">《CANN 官方镜像仓库》</a>。
请选用类似以下版本的 `openEuler` 镜像：`9.0.0-xxx-openeuler24.03-py3.11`（其中 xxx 需根据您的昇腾 AI 处理器型号填写）。
以Atlas A2 训练系列产品/Atlas A2 推理系列产品
为例，拉取命令如下：

```shell
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-beta.2-910b-openeuler24.03-py3.11
```

### 场景二：针对老旧操作系统的打包与部署

请依据您的具体环境，从华为云官方容器镜像仓库获取相应的算子开发编译专用 Docker 镜像。

- **x86 架构**：

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:x86_20260211_v01
```

- **arm 架构**：

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:arm_20260211_v01
```

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
python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-beta.2-910b-openeuler24.03-py3.11
```

**预期输出：**    
启动成功后将直接进入容器，终端显示容器内的命令行提示符，等待输入命令:

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

### 3.1. 场景一的环境配置

进入容器后，执行如下命令：

```shell
yum install ninja-build -y
yum install pigz -y
```

### 3.2 场景二的环境配置

执行以下命令，将 CANN 环境变量配置写入 `~/.bashrc` 文件，以确保其永久生效：

```shell
echo "source /usr/local/Ascend/cann/set_env.sh" >> ~/.bashrc
source ~/.bashrc
```

## 4. FAQ

### 4.1 下载依赖时多次提示输入密码，如何仅输入一次？

可通过以下命令配置并保存 Git 凭证：

```shell
git config --global credential.helper store
```
