# 昇腾 CANN 容器环境安装指南

<br>

本指南基于**昇腾 CANN 官方镜像**，帮助您通过 Docker 容器化方式，快速搭建面向昇腾 AI 的算子开发环境。

## 前置条件

请确保以下环境已就绪：

| 条件            | 说明                     | 验证命令         |
|----------------|------------------------|----------------|
| Docker Engine  | 已安装且守护进程正在运行       | `docker info`  |

满足上述条件后，完整部署通常 **5 分钟内完成**（取决于网络速度）；若本地已有 CANN 镜像，则可 **秒级完成启动**。

<br>

## 1. 获取 CANN 开发镜像

> [!CAUTION]注意   
> 算子开发**必须**使用带有 `-devel` 后缀的镜像（包含完整的编译工具链）。请勿使用普通运行时镜像。

### 1.1 查询本地镜像

运行以下命令检查是否已存在 CANN 开发镜像：

```bash
docker images | grep cann | grep devel
```

示例输出：

```text
REPOSITORY                                          TAG                                               IMAGE ID            CREATED             SIZE
swr.cn-south-1.myhuaweicloud.com/ascendhub/cann     9.0.0-910b-openeuler24.03-py3.11-devel            6df0c5bbc16f        2 weeks ago         11.9GB
```

若已有合适版本，可直接跳转至 [第 2 节：启动容器](#2-启动容器)。

### 1.2 拉取 CANN 镜像

#### 1.2.1 获取镜像下载命令

1. 访问 [CANN 镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)，切换至 **"镜像下载"** 标签页，浏览可用版本列表（可通过右侧的搜索框过滤）：

    ![image.png](https://raw.gitcode.com/user-images/assets/9310220/32504999-0da1-4595-8865-acd9a01cfd3b/image.png 'image.png')

2. 根据以下建议选择镜像版本：

    | 选项          | 建议                                               |
    | ----------- | ------------------------------------------------ |
    | **CANN 版本** | 若无特殊需求，建议选用最新稳定版本                                |
    | **芯片型号**    | 根据实际硬件选择（执行 `npu-smi info` 查看） |
    | **操作系统**    | openEuler 或 Ubuntu 均可              |
    | **开发专用**    | 应选择带有 `-devel` 后缀的版本，该版本包含算子开发所需的完整软件环境               |

    > [!CAUTION] 注意  
    > 必须使用带 `-devel` 后缀的镜像（如 `...-py3.11-devel`），否则无法编译自定义算子。

3. 点击“立即下载”，复制生成的 `docker pull` 命令。

    ![image.png](https://raw.gitcode.com/user-images/assets/9310220/0b35b9a5-b9c4-4c42-a25d-31432c6611d2/image.png 'image.png')

#### 1.2.2 在线拉取（服务器具备外网访问能力）

请直接执行复制的命令。示例如下（耗时约 3～5 分钟，具体取决于网络带宽与延迟）：

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
```

镜像拉取完成后，请跳转至 [第 2 节：启动容器](#2-启动容器)。

#### 1.2.3 离线导入（服务器无外网访问权限）

若服务器无法直接访问华为云容器镜像仓库（例如处于企业内网等隔离网络环境），请按以下步骤操作：

1. 在具备外网访问能力的主机上拉取镜像（注意架构匹配 x86/ARM）：

   ```bash
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
   ```
 
2. 导出为 tar 文件：

   ```bash
   docker save -o cann.tar swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
   ```
   
3. 通过 U 盘或中转网络等方式将 `cann.tar` 传至服务器，并加载：
   
   ```bash
   docker load -i cann.tar
   ```

可通过执行 `docker images` 命令查看是否已成功加载，加载后的镜像与在线拉取结果完全一致。

<br>

## 2. 启动容器

### 2.1 下载容器启动脚本

执行以下命令，将启动脚本下载至 HOME 目录：

```bash
cd ~ && curl -fLO --retry 10 --retry-all-errors --retry-delay 3 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" https://raw.gitcode.com/Ascend/msot/raw/master/example/quick_start/public/ctr_in.py && chmod +x ctr_in.py
```

> [!NOTE] 说明
> 1.若提示 `--retry-all-errors` 参数不存在，说明 curl 版本过低，可移除该参数后重试。  
> 2.若多次下载仍失败，可能触发了 CDN 的反爬虫防护机制，可手动从仓库下载 [ctr_in.py](../../../example/quick_start/public/ctr_in.py) 文件。  
> 3.若您的服务器处于企业内网等无法直连外网的环境，可先在当前访问此文档页面的设备上下载该文件，再通过 U 盘或中转网络等方式将其传至服务器。

### 2.2 执行启动命令

**参数说明：**

| 参数               | 说明                                   | 示例              |
| ---------------- | ------------------------------------ | --------------- |
| `CONTAINER_NAME` | 容器名称，后续可通过该名称登录容器，建议格式：`{用途}_{个人标识}` | `op_dev_alice` |
| `USER_NAME`      | 宿主机用户名，用于挂载 `$HOME` 目录实现数据共享         | `alice`         |
| `IMAGE`          | Docker 镜像 ID 或完整名称                   | `6df0c5bbc16f`  |

**命令格式：**

```bash
python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>
```

**执行示例：**

```bash
# 使用镜像 ID
python3 ~/ctr_in.py op_dev_alice alice 6df0c5bbc16f

# 使用镜像全名
python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel
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
