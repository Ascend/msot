# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

> [!CAUTION]注意
> 本文档及相关脚本仅供学习使用，不承诺生产环境的稳定性和安全性，使用者需自行评估风险并承担相应责任。

## 前置条件

开始安装前，请确认服务器满足以下要求：

| 项目 | 要求                           |
|------|------------------------------|
| 操作系统 | Linux                        |
| NPU 卡 | 至少 1 张（基于昇腾 910B 或 昇腾 A3 芯片） |
| 已安装软件 | NPU 驱动、固件、Docker 服务、Python 3、curl、git |

> **网络要求：** 主路径步骤需要外网访问以拉取镜像和脚本；如在内网环境，请参阅 [FAQ 4.2](#42-服务器无外网访问权限如何部署) 解决。

## 1. 安装算子开发工具链（CANN 容器）

> [!NOTE]说明
> 
> - 昇腾 AI 算子开发工具链随 CANN 统一发布，安装 CANN 即完成工具链安装。
> - 由于算子编译环境依赖较为复杂，本教程**仅支持** CANN 容器环境，不支持裸机或虚拟机等非容器化部署方式。

### 1.1 获取 CANN 官方容器镜像

#### 1.1.1 设置镜像变量

根据实际使用的芯片类型，执行对应命令（本学习环境只支持昇腾 910B 和 昇腾 A3 芯片）：

```bash
# 昇腾 910B 芯片
export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11-devel

# 昇腾 A3 芯片
export MY_STUDY_VAR_CANN_IMAGE=swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-a3-openeuler24.03-py3.11-devel
```

#### 1.1.2 拉取镜像

```bash
docker pull ${MY_STUDY_VAR_CANN_IMAGE}
```

### 1.2 启动容器

#### 1.2.1 下载容器启动脚本

```bash
cd ~ && curl -O https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
```

#### 1.2.2 启动容器

```bash
~/ctr_in.py ${MY_STUDY_VAR_CANN_IMAGE}
```

**预期输出：** 出现类似 [root@xxxxxx ~]# 的 root shell 提示符，即表示容器启动成功。

> [!NOTE]说明  
> 从现在起，以下所有操作均需在容器内的 shell 中执行。

## 2. 克隆示例代码仓

在容器内将代码仓克隆至 `~/ot_demo/msot` 目录：

```bash
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

克隆完成后，示例代码路径为 `~/ot_demo/msot/example`。

## 3. 设置芯片 SoC 型号

后续多条命令均需引用芯片 SoC 型号（片上系统型号，用于标识芯片架构），此处统一查询并保存到环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`，便于后续直接使用，在容器内执行：

```bash
# acl 模块随 CANN 安装
export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace('Ascend', ''))")
```

> [!CAUTION]注意
> 环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 和 `MY_STUDY_VAR_CANN_IMAGE` 仅用于本快速入门学习，请勿在商用开发中使用。

至此，学习环境安装完成。接下来，请返回快速入门文档继续操作。

## 4. 常见问题（FAQ）

### 4.1 退出容器后如何重新进入？

**1.快捷方式**：执行 `~/ctr_in.py`，交互式选择要进入的容器（若只有一个则直接进入）。  
**2.原生命令**：执行 `docker exec -it alice_YYMMDD_HHMMSS bash`（将容器名替换为实际名称）。

### 4.2 服务器无外网访问权限，如何部署？

若服务器处于隔离内网，可参照以下方法完成对应需要外网步骤的准备工作：

**1. 离线导入 CANN 镜像**

在有外网且 CPU 架构与目标服务器相同的机器上执行：

```bash
# 拉取镜像（提前按1.1.1节提前设置好环境变量）
docker pull ${MY_STUDY_VAR_CANN_IMAGE}

# 导出为 tar 包
docker save -o cann.tar ${MY_STUDY_VAR_CANN_IMAGE}
```

将 `cann.tar` 传输至内网服务器后，执行以下命令加载镜像：

```bash
docker load -i cann.tar
```

加载完成后，执行 `docker images` 验证镜像是否已成功导入。

**2. 传输容器启动脚本**

在有网络的机器上按 [1.2.1节](#121-下载容器启动脚本) 下载 `ctr_in.py`，然后手动拷贝至内网服务器的 `~/` 目录。

**3. 同步示例代码仓**

在有网络的机器上按 [第2节](#2-克隆示例代码仓) 克隆代码仓，然后将整个 `msot` 目录拷贝至内网服务器的对应工作路径。

### 4.3 重新进入容器后环境变量丢失，如何处理？

`export` 命令设置的环境变量仅在当前 shell 会话中有效，退出容器后即失效。重新进入容器时，需重新执行 `export` 命令恢复变量。  
如想避免每次手动执行，可将上述 `export` 命令追加到容器内的 `~/.bashrc` 文件末尾，后续进入容器时将自动生效。
