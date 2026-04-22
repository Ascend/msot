# 昇腾 CANN 容器环境安装指南

<br>

本指南基于 **昇腾 CANN 官方镜像**，帮助您通过 Docker 容器化方式快速搭建面向昇腾 AI 算子开发环境。

> [!CAUTION] 注意
> **免责声明**
> 本文档及相关脚本仅供学习参考，不保证生产环境的稳定性与安全性，使用者需自行评估风险并承担相应责任。
 
## 前置条件

在开始之前，请确认以下环境已就绪：

| 条件            | 说明              | 验证命令           |
| ------------- | --------------- | -------------- |
| Docker Engine | 已安装且守护进程处于运行状态  | `docker info`  |
| 网络连通性        | 可访问华为云镜像仓库，用于拉取镜像与下载脚本 | `ping swr.cn-south-1.myhuaweicloud.com` |

满足以上前置条件后，按本文完成环境搭建与容器启动通常仅需 **5 分钟** 以内（视网速而定）；若本地已有 CANN 镜像，则**秒级**即可完成。

<br>

## 1. 准备镜像

### 1.1 查询本地已有镜像

执行以下命令查询当前环境中已有的 CANN 镜像：

```shell
docker images | grep cann
```

若返回结果中包含 CANN 镜像，示例输出如下：

```text
REPOSITORY                                          TAG                                               IMAGE ID            CREATED             SIZE
swr.cn-south-1.myhuaweicloud.com/ascendhub/cann     8.5.1-910b-openeuler24.03-py3.11                  6df0c5bbc16f        2 weeks ago         17.1GB
```

若已有合适版本，可直接跳转至 [第 2 节：启动容器](#2-启动容器)。

### 1.2 拉取 CANN 镜像

若本地无可用镜像，请按以下步骤操作。

**Step 1** — 访问 [CANN 镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)，切换至 **"镜像版本"** 标签页，浏览可用版本列表：

![image.png](https://raw.gitcode.com/user-images/assets/8763895/f2a0ae4f-4a7a-4c0e-ada9-ec4a0ab71403/image.png 'image.png')   

**Step 2** — 根据以下建议选择镜像版本：

| 选项          | 建议                                               |
| ----------- | ------------------------------------------------ |
| **CANN 版本** | 若无特殊需求，建议选用最新稳定版本                                |
| **芯片型号**    | 根据实际硬件选择（执行 `npu-smi info` 查看） |
| **操作系统**    | openEuler 或 Ubuntu 均可，推荐 openEuler               |

**Step 3** — 复制完整的镜像版本号（例如：8.5.1-910b-openeuler24.03-py3.11），按如下格式拼接拉取命令：

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:<镜像版本号>
```

执行示例（耗时约 3~5 分钟，视网络状况而定）：

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11
```

> [!NOTE] 说明
> **为什么镜像名（swr.cn-south-1.myhuaweicloud.com/ascendhub/cann）这么长？**    
> 因为全路径格式包含了完整的注册中心地址，可直接拉取而无需额外配置 Docker Registry，实现开箱即用。

<br>

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
python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11
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
