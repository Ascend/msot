# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

> [!CAUTION]注意
> 本文档及相关脚本仅供学习用途，不保证在生产环境中的稳定性与安全性。使用者须自行评估相关风险，并承担全部责任。

## 1. 前置条件

在开始安装前，请确保服务器满足以下要求。本章命令均在**宿主机**执行：

| 项目   | 要求                                                                  | 验证方法                           |
|------|---------------------------------------------------------------------|--------------------------------|
| **硬件算力** | Linux 服务器配备至少 1 张 NPU 卡（基于昇腾 910B/310P/A3 芯片，**推荐 910B**），驱动与固件已正确安装 | 执行 `npu-smi info`，确认 NPU 卡状态正常 |
| **容器运行** | 已安装并运行 Docker（建议版本 ≥ 18.x）                                          | 执行 `docker ps`，无报错即表示服务正常启动    |
| **执行用户** | 使用普通用户账户启动容器                                                        | 执行 `whoami`，返回非 `root` 的用户名    |
| **脚本执行** | 已安装 Python 3（任意版本）                                                  | 执行 `python3 -V`，有版本信息输出即表示已安装  |
| **网络通信** | 已安装 curl（任意版本）                                                      | 执行 `curl -V`，有版本信息输出即表示已安装     |

> 👉 确认前置条件满足后，若环境具备公网访问能力，后续命令可全程直接 **Copy/Paste** 执行，无需手动输入或拼接，以避免因输入错误导致命令执行失败。

## 2. 宿主机：选择并拉取 CANN 镜像

> [!NOTE]说明
>
> - 昇腾 AI 算子开发工具链随 CANN 统一发布，安装 CANN 即完成工具链部署。
> - 鉴于算子编译环境依赖复杂，本教程**仅支持** CANN 容器化部署方式，不支持裸机或虚拟机等非容器环境。

### 2.1 基于芯片型号自动识别并配置镜像环境变量

在宿主机执行以下命令，系统将根据当前 NPU 芯片型号自动匹配对应的 CANN 镜像，并将其名称写入可复用的环境变量，供后续流程调用：

```bash
source /dev/stdin <<< "$(dev_id=$(lspci -n -D | grep -o '19e5:d[0-9a-f]\{3\}' | head -n1 | cut -d: -f2); case "$dev_id" in 'd500' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-310p-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=310P";; 'd802' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=910B";; 'd803' ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-a3-openeuler24.03-py3.11-devel; export MY_CHIP_NAME=A3";; * ) echo "unset MY_STUDY_VAR_CANN_IMAGE MY_CHIP_NAME; echo >&2; echo -e '\033[31m[FAIL] Get device ID: $dev_id. Learning is not supported in the current environment.\033[0m' >&2";; esac)"
[ -n "$MY_STUDY_VAR_CANN_IMAGE" ] && echo -e "\e[32m[PASS] Successfully identified chip [$MY_CHIP_NAME] and auto-selected image:\n    $MY_STUDY_VAR_CANN_IMAGE\e[0m"
```

> [!NOTE]说明
>
> **命令原理**  
> 通过 `lspci` 获取 NPU 的 PCI ID，自动匹配 CANN 官方镜像，并将镜像地址赋给环境变量 `MY_STUDY_VAR_CANN_IMAGE`，供后续使用。  
> 所有镜像均来自华为云 AscendHub 上发布的 CANN 官方镜像。如需了解镜像详情，请参阅 [CANN 官方镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)。

若命令执行后输出 `[PASS]`，则表示执行成功；若输出 `[FAIL]`，可能原因如下：

1. 硬件不在本教程支持范围内：本学习环境仅支持昇腾 910B、310P 及 A3 系列芯片，请切换至兼容的硬件环境后重试；
2. 底层环境异常：未安装 `lspci`，或当前用户无法通过 `lspci -n -D` 查询 NPU PCI ID，请联系环境管理员确认底层环境。

### 2.2 拉取镜像

在宿主机执行：

```bash
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
```

若因处于企业内网导致拉取失败，请参考 [8.1 节](#81-docker-镜像在隔离内网的获取方法) 的解决方案。

## 3. 宿主机：下载脚本并启动容器

### 3.1 下载容器启动脚本

在宿主机执行：

```bash
cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

若因网络限制无法下载，请参考 [8.2 节](#82-传输容器启动脚本) 的解决方案。

### 3.2 启动容器

在宿主机执行以下命令，根据提示确认容器创建信息后，直接回车即可：

```bash
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

**预期输出**：出现类似如下提示信息，并停留在 root Shell 提示符，表示容器已成功启动：

```text
Welcome to 5.10.0-60.139.0.166.oe2203.aarch64

System information as of time:  Mon Jun 29 15:21:01 UTC 2026

System load:    8.44
Memory used:    1.5%
Swap used:      0%
Usage On:       27%
Users online:   0

[root@xxxxxx ~]#
```

若提示错误或出现容器选择界面，请参考 [2.1 节](#21-基于芯片型号自动识别并配置镜像环境变量) 确认环境变量 `MY_STUDY_VAR_CANN_IMAGE` 是否正确，并重新执行命令。

> [!CAUTION]注意
>
> 看到容器内 Shell 提示符后，后续第 4 章至第 6 章的命令均应在**容器内部**执行。

## 4. 容器内：克隆示例代码仓库

在容器内将示例代码克隆至 `~/ot_demo/msot` 目录：

```bash
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

克隆完成后，示例代码路径为 `~/ot_demo/msot/example`。若因网络问题导致克隆失败，请参考 [8.3 节](#83-传输示例代码仓库) 的解决方案。

## 5. 容器内：设置芯片 SoC 型号

后续多条命令需引用芯片 SoC 型号（片上系统型号，用于标识芯片架构）。此处统一查询并保存到环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`，便于后续直接调用。  

在容器内执行如下命令：

```bash
echo 'export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace(\"Ascend\", \"\"))")' > /etc/profile.d/custom-env.sh && chmod +x /etc/profile.d/custom-env.sh && source /etc/profile.d/custom-env.sh && { [ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e '\033[31m[FAIL] Failed to set environment variable $MY_STUDY_VAR_CHIP_SOC_TYPE!\033[0m'; }
```

若显示 `[PASS]`，表示设置成功；若显示 `[FAIL]`，通常是因为未成功部署 CANN 容器，或误在宿主机（容器外）执行了本步骤，请确认已进入容器后重试。

> [!CAUTION]注意
> 环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 与 `MY_STUDY_VAR_CANN_IMAGE` 仅适用于本快速入门教程，请勿在商业开发中使用。

## 6. 安装完成自检

在容器内执行以下命令，确认快速入门所需环境已准备完成：

```bash
[ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e "\033[31m[FAIL] Missing environment variable MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m"
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] Example code repository OK\033[0m" || echo -e "\033[31m[FAIL] Example code repository missing\033[0m"
```

若以上检查均输出 `[PASS]`，则学习环境安装完成。接下来，请返回快速入门文档继续后续操作。

<br>

## 7. 常见问题（FAQ）

### 7.1 退出容器后如何重新进入？

在宿主机执行以下任一命令：

**方法一（推荐）**：执行 `~/ctr_in.py`，交互式选择目标容器（若仅有一个容器则自动进入）。

**方法二（原生命令）**：执行 `docker exec -it alice_YYMMDD_HHMMSS bash`（请替换为实际容器名称）。

### 7.2 执行 Docker 命令遇到 permission denied 类错误提示？

可能当前用户未加入 Docker 用户组。可使用 root 权限在宿主机执行：

```bash
sudo usermod -aG docker <当前用户名>
```

执行后需要重新登录当前用户会话，或执行 `newgrp docker` 使用户组变更立即生效。不建议以 root 身份进行日常操作。

## 8. 内网环境无公网访问权限的应对方案

### 8.1 Docker 镜像在隔离内网的获取方法

**方案一：配置 Docker 代理直接拉取**

适用于大多数 Linux 发行版且 Docker 版本 ≥ 18 的环境（不保证所有场景兼容）。若遇异常，请结合实际情况调整。

编辑 Docker 服务代理配置文件 `/etc/systemd/system/docker.service.d/http-proxy.conf`，内容示例如下（请根据实际环境替换用户名、密码、代理地址及端口）：

```text
[Service]
Environment="HTTP_PROXY=http://username:password@proxy.example.com:8080"
Environment="HTTPS_PROXY=http://username:password@proxy.example.com:8080"
Environment="NO_PROXY=localhost,127.0.0.1,.example.com"
```

保存后重载并重启 Docker 服务：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

随后即可正常执行 `docker pull`。

**方案二：离线导入 CANN 镜像**

如果代理方案不可行，请先在内网 NPU 服务器上执行 [2.1 节](#21-基于芯片型号自动识别并配置镜像环境变量)，根据当前芯片型号得到环境变量 `MY_STUDY_VAR_CANN_IMAGE` 的值；再将该镜像名复制到具备公网且 CPU 架构相同的机器上，执行如下命令：

```bash
docker pull <MY_STUDY_VAR_CANN_IMAGE>
docker save -o cann.tar <MY_STUDY_VAR_CANN_IMAGE>
```

将 `cann.tar` 通过 U 盘等方式传输至内网服务器后，在内网服务器执行以下命令加载：

```bash
docker load -i cann.tar
docker images | grep cann
```

加载完成后，返回 [第 3 章](#3-宿主机下载脚本并启动容器) 启动容器。

### 8.2 传输容器启动脚本

在可访问当前网页的浏览器中输入如下链接，下载 `ctr_in.py` 脚本文件，并将其手动拷贝至内网服务器的 `~/` 目录：

```text
https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py
```

拷贝完成后，在内网服务器的宿主机上执行：

```bash
cd ~
chmod +x ctr_in.py
ls -l ctr_in.py
```

确认 `ctr_in.py` 存在且具有执行权限后，返回 [3.2 节](#32-启动容器) 启动容器。

### 8.3 传输示例代码仓库

在可访问当前网页的浏览器中输入如下链接，进入页面后点击“下载 zip”按钮，将代码仓库压缩包下载至本地：

```text
https://gitcode.com/Ascend/msot
```

将下载得到的 zip 包传输至内网服务器的容器内的 `~` 目录（可以通过 `docker cp` 命令、挂载目录、网络传输等各种方法传输至容器内）。

在容器内执行以下命令解压，请将 `<MSOT_ZIP>` 替换为实际 zip 包文件名：

```bash
unzip <MSOT_ZIP> -d ~/ot_demo
```

再执行以下命令，将示例代码仓库移动至 `~/ot_demo/msot` 目录并确认目录位置正确：

```bash
mv ~/ot_demo/msot-* ~/ot_demo/msot
ls ~/ot_demo/msot/example/quick_start
```

若 `ls` 命令不报错，则示例代码仓库同步完成。随后返回 [第 5 章](#5-容器内设置芯片-soc-型号) 设置芯片 SoC 型号。
