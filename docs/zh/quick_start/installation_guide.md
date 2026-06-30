# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

> [!CAUTION]注意
> 本文档及相关脚本仅用于学习目的，不保证在生产环境中的稳定性与安全性。使用者应自行评估相关风险并承担全部责任。

## 前置条件

开始安装前，请确保服务器满足以下要求：

| 项目 | 要求 | 验证方法 |
|------|------|----------|
| 操作系统 | Linux | `uname -s` 显示 `Linux` |
| NPU 卡 | 至少 1 张（基于昇腾 910B 或 310P 芯片，**推荐使用 910B**），驱动、固件安装好 | `npu-smi info` 能正常显示卡信息 |
| Docker 服务 | 已安装并启动 | `docker ps` 能正常执行（无报错即表示服务已启动） |
| 其他软件 | Python 3、curl、git | 分别执行 `python3 --version`、`curl --version`、`git --version`，均有版本输出即可 |

## 1. 安装算子开发工具链（CANN 容器）

> [!NOTE]说明  
> 
> - 昇腾 AI 算子开发工具链随 CANN 统一发布，安装 CANN 即完成工具链安装。
> - 鉴于算子编译环境依赖复杂，本教程**仅支持** CANN 容器化部署方式，不适用于裸机或虚拟机等非容器环境。
> - 本节（1.1~1.2）所有命令均在**宿主机**执行；进入容器后的操作从第 2 节开始。

### 1.1 获取 CANN 官方容器镜像

#### 1.1.1 设置镜像变量

根据所用芯片类型执行对应命令（本学习环境仅支持昇腾 910B 与 310P 系列）：

```bash
# 昇腾 910B 系列芯片
export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel

# 昇腾 310P 系列芯片
export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-310p-openeuler24.03-py3.11-devel
```

> [!NOTE]说明
> 
> **如何确定应使用哪个镜像？**  
> 可通过执行 `npu-smi info` 命令判断。例如，在以下输出中，若 Name 列（芯片名称）包含 “910B” 字样，则选择 910B 镜像；若包含 “310P”，则选择 310P 镜像：
> 
> ```text
>+------------------------------------------------------------------------------------------------+
>| npu-smi 25.5.0                   Version: 25.5.0                                               |
>+---------------------------+---------------+----------------------------------------------------+
>| NPU   Name                | Health        | Power(W)    Temp(C)           Hugepages-Usage(page)|
>| Chip                      | Bus-Id        | AICore(%)   Memory-Usage(MB)  HBM-Usage(MB)        |
>+===========================+===============+====================================================+
>| 0     910B4               | OK            | 94.0        39                0    / 0             |
>| 0                         | 0000:C1:00.0  | 0           0    / 0          2880 / 32768         |
>+===========================+===============+====================================================+
> ```

#### 1.1.2 拉取镜像

```bash
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
```

若因处于企业内网导致拉取失败，请参考 [5.1 节](#51-docker-镜像获取) 的解决方案。

### 1.2 启动容器

#### 1.2.1 下载容器启动脚本

```bash
cd ~ && curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

若因网络限制无法下载，请参考 [5.2 节](#52-传输容器启动脚本)。

#### 1.2.2 启动容器

```bash
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

**预期输出**：出现如下提示信息，并停留在 root shell 提示符，表示容器已成功启动：

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

> [!NOTE]说明  
> 自此步骤起，后续所有操作均应在容器内部的 shell 中执行。

## 2. 克隆示例代码仓库

在容器内将示例代码克隆至 `~/ot_demo/msot` 目录：

```bash
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

克隆完成后，示例代码路径为 `~/ot_demo/msot/example`。

若因网络问题导致克隆失败，请参考 [5.3 节](#53-同步示例代码仓库)。

## 3. 设置芯片 SoC 型号

后续多条命令均需引用芯片 SoC 型号（片上系统型号，用于标识芯片架构），此处统一查询并保存到环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`，便于后续直接使用，在容器内执行：

```bash
# acl 模块随 CANN 安装
export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace('Ascend', ''))")

# 校验是否设置成功
[ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] 芯片型号: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e "\033[31m[FAIL] 环境变量 \$MY_STUDY_VAR_CHIP_SOC_TYPE 设置失败！\033[0m"
```

若显示 [PASS] 即表示设置成功；若显示 [FAIL]，通常是因为未成功部署 CANN 容器，或误在宿主机（容器外）执行了本步骤——请确认已进入容器后重试。

> [!CAUTION]注意
> 环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 与 `MY_STUDY_VAR_CANN_IMAGE` 仅适用于本快速入门教程，请勿在商业开发中使用。

至此，学习环境安装完成。接下来，请返回快速入门文档继续后续操作。

## 4. 常见问题（FAQ）

### 4.1 退出容器后如何重新进入？

**方法一（推荐）**：执行 `~/ctr_in.py`，交互式选择目标容器（若仅有一个容器则自动进入）。  
**方法二（原生命令）**：执行 `docker exec -it alice_YYMMDD_HHMMSS bash`（请替换为实际容器名称）。

### 4.2 重新进入容器后环境变量丢失，如何处理？

通过 `export` 设置的环境变量仅在当前 shell 会话中有效，退出容器后将失效。重新进入后需再次执行 `export` 命令。  
如需持久化，可将相关 `export` 命令追加至容器内 `~/.bashrc` 文件末尾，使变量在每次登录时自动加载。

### 4.3 执行 docker 命令遇到 permission denied 类错误提示？

可能当前用户不在 docker 组，用 root 权限执行 `usermod -aG docker <当前用户名>`，不建议切为 root 进行体验。

## 5. 内网环境无外网访问权限的应对方案

### 5.1 Docker 镜像获取

**方案一：配置 Docker 代理直接拉取**

适用于大多数 Linux 发行版且 Docker 版本 ≥18 的环境（不保证所有场景兼容）。若遇异常，请结合实际情况调整。

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

在具备外网且 CPU 架构相同的机器上执行：

```bash
# 拉取镜像（需先按 1.1.1 节设置环境变量）
docker pull ${MY_STUDY_VAR_CANN_IMAGE}

# 导出为 tar 包
docker save -o cann.tar ${MY_STUDY_VAR_CANN_IMAGE}
```

将 `cann.tar` 传输至内网服务器后，执行以下命令加载：

```bash
docker load -i cann.tar
```

加载完成后，可通过 `docker images` 验证镜像是否导入成功。

### 5.2 传输容器启动脚本

在访问当前网页的浏览器中输入如下链接，下载 `ctr_in.py` 脚本文件，并将其手动拷贝至内网服务器的 `~/` 目录，随后执行权限设置命令 `chmod +x ctr_in.py`。

```text
https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py
```

### 5.3 同步示例代码仓库

在访问当前网页的浏览器中输入如下链接，进入页面后点击“下载zip”按钮，将代码仓库压缩包下载至本地，再将其拷贝至内网服务器的目标工作目录，确保路径为 `~/ot_demo/msot/example`。

```text
https://gitcode.com/Ascend/msot
```
