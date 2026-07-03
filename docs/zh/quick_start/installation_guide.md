# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

> [!CAUTION]注意
> 本文档及相关脚本仅供学习用途，不保证在生产环境中的稳定性与安全性。使用者须自行评估相关风险，并承担全部责任。

## 前置条件

开始安装前，请确保服务器满足以下要求：

| 项目 | 要求                                              | 验证方法                                 |
|------|-------------------------------------------------|--------------------------------------|
| 操作系统 | Linux                                           | `uname -s` 输出为 `Linux`               |
| NPU 卡 | 至少 1 张（基于昇腾 910B/310P/A3 芯片，**推荐使用 910B**），驱动与固件已正确安装 | `npu-smi info` 可正常显示设备信息             |
| Docker 服务 | 已安装并处于运行状态                                | `docker ps` 可正常执行（无报错即表示服务已启动）       |
| 其他软件 | Python 3、curl                                 | 分别执行 `python3 -V`、`curl -V` 均有有效版本输出 |

> 👉 确认前置条件满足后，若环境具备互联网访问能力，后续命令可全程直接 **复制粘贴（Copy/Paste）** 执行，无需手动输入或拼接，以避免因输入错误导致命令执行失败。

## 1. 安装算子开发工具链（CANN 容器）

> [!NOTE]说明  
> 
> - 昇腾 AI 算子开发工具链随 CANN 统一发布，安装 CANN 即完成工具链部署。
> - 鉴于算子编译环境依赖复杂，本教程**仅支持** CANN 容器化部署方式，不适用于裸机或虚拟机等非容器环境。

### 1.1 获取 CANN 官方容器镜像

#### 1.1.1 设置镜像变量

执行以下命令，根据当前 NPU 芯片型号自动配置镜像信息环境变量：

```bash
source /dev/stdin <<< "$(chip=$(npu-smi info -m 2>/dev/null | grep -oP 'Ascend\s*\S+' | head -1); case "$chip" in 'Ascend 910B'* ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel; echo '[PASS] Successfully identified chip [$chip] and completed environment configuration.'";; 'Ascend910'* ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-a3-openeuler24.03-py3.11-devel; echo '[PASS] Successfully identified chip [$chip] and completed environment configuration.'";; 'Ascend 310P'* ) echo "export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-310p-openeuler24.03-py3.11-devel; echo '[PASS] Successfully identified chip [$chip] and completed environment configuration.'";; * ) echo "echo >&2; echo -e '\033[31m[FAIL] Get chip: $chip. Learning is not supported in the current environment.\033[0m' >&2";; esac)"
[ -n "$MY_STUDY_VAR_CANN_IMAGE" ] && echo -e "\n\e[32m[PASS] Auto-selected image for detected chip:\n    $MY_STUDY_VAR_CANN_IMAGE\e[0m"
```

> [!NOTE]说明
> 
> **命令原理说明**  
> 通过 `npu-smi info` 获取 NPU 芯片型号，依据硬件信息自动匹配对应的镜像，并将结果赋值给环境变量 `MY_STUDY_VAR_CANN_IMAGE`，供后续容器启动等操作使用。  
> 所用镜像均源自华为云镜像仓库中 CANN 发布的官方镜像，如需了解镜像的详细信息，请访问 [CANN 官方镜像仓库](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884)。

若命令执行后输出 `[PASS]`，则表示执行成功；若输出为 `[FAIL]`，可能原因如下：  

1. NPU 环境异常导致 `npu-smi info` 命令执行失败，请联系环境管理员修复底层环境问题；  
2. 当前硬件不在本教程支持范围内，本学习环境仅支持昇腾 910B、310P 及 A3 系列芯片，请切换至兼容的硬件环境后重试。

#### 1.1.2 拉取镜像

```bash
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
```

若因处于企业内网导致拉取失败，请参考 [5.1 节](#51-docker-镜像在隔离内网的获取方法) 的解决方案。

### 1.2 启动容器

#### 1.2.1 下载容器启动脚本

```bash
cd ~ && curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

若因网络限制无法下载，请参考 [5.2 节](#52-传输容器启动脚本) 的解决方案。

#### 1.2.2 启动容器

```bash
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

**预期输出**：出现类似如下提示信息，并停留在 root shell 提示符，表示容器已成功启动：

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

> [!CAUTION]注意  
> 
> **自此步骤起，后续所有操作均应在容器内部的 shell 中执行。**

## 2. 克隆示例代码仓库

在容器内将示例代码克隆至 `~/ot_demo/msot` 目录：

```bash
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

克隆完成后，示例代码路径为 `~/ot_demo/msot/example`。

若因网络问题导致克隆失败，请参考 [5.3 节](#53-同步示例代码仓库) 的解决方案。。

## 3. 设置芯片 SoC 型号

后续多条命令需引用芯片 SoC 型号（片上系统型号，用于标识芯片架构）。此处统一查询并保存至环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`，便于后续直接调用。在容器内执行：

```bash
echo 'export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace(\"Ascend\", \"\"))")' > /etc/profile.d/custom-env.sh && chmod +x /etc/profile.d/custom-env.sh && source /etc/profile.d/custom-env.sh && { [ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip SoC type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e '\033[31m[FAIL] Failed to set environment variable $MY_STUDY_VAR_CHIP_SOC_TYPE!\033[0m'; }
```

若显示 `[PASS]`，表示设置成功；若显示 `[FAIL]`，通常是因为未成功部署 CANN 容器，或误在宿主机（容器外）执行了本步骤，请确认已进入容器后重试。

> [!CAUTION]注意
> 环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 与 `MY_STUDY_VAR_CANN_IMAGE` 仅适用于本快速入门教程，请勿在商业开发中使用。

至此，学习环境安装完成。接下来，请返回快速入门文档继续后续操作。

<br>

## 4. 常见问题（FAQ）

### 4.1 退出容器后如何重新进入？

**方法一（推荐）**：执行 `~/ctr_in.py`，交互式选择目标容器（若仅有一个容器则自动进入）。  
**方法二（原生命令）**：执行 `docker exec -it alice_YYMMDD_HHMMSS bash`（请替换为实际容器名称）。

### 4.2 执行 docker 命令遇到 permission denied 类错误提示？

可能当前用户未加入 docker 用户组。可使用 root 权限执行 `usermod -aG docker <当前用户名>`，不建议以 root 身份进行日常操作。

## 5. 内网环境无外网访问权限的应对方案

### 5.1 Docker 镜像在隔离内网的获取方法

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

如果代理服务器方案不可行，可在具备外网且 CPU 架构相同的机器上执行：

```bash
# 拉取镜像（需先按 1.1.1 节设置环境变量）
docker pull ${MY_STUDY_VAR_CANN_IMAGE}

# 导出为 tar 包
docker save -o cann.tar ${MY_STUDY_VAR_CANN_IMAGE}
```

将 `cann.tar` 通过优盘等方式传输至内网服务器后，执行以下命令加载：

```bash
docker load -i cann.tar
```

加载完成后，可通过 `docker images` 验证镜像是否导入成功。

### 5.2 传输容器启动脚本

在可访问当前网页的浏览器中输入如下链接，下载 `ctr_in.py` 脚本文件，并将其手动拷贝至内网服务器的 `~/` 目录，随后执行权限设置命令 `chmod +x ctr_in.py`。

```text
https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py
```

### 5.3 同步示例代码仓库

在可访问当前网页的浏览器中输入如下链接，进入页面后点击“下载zip”按钮，将代码仓库压缩包下载至本地，再将其拷贝至内网服务器的目标工作目录，确保路径为 `~/ot_demo/msot/example`。

```text
https://gitcode.com/Ascend/msot
```
