# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

> [!CAUTION]注意   
> 本文档及相关脚本仅供学习使用，不承诺生产环境的稳定性和安全性，使用者需自行评估风险并承担相应责任。

您需要准备一台 Linux 服务器，配备至少 1 张昇腾 NPU 卡，且已安装好 NPU 驱动、固件和 Docker 服务。

## 1. 算子开发工具链安装

👉 **【关键安装步骤】请严格遵照《[CANN 容器环境安装指南](./cann_container_setup.md)》完成安装。Docker 服务正常时，5 分钟内可完成。** 

> [!NOTE] 说明
> 昇腾 AI 算子开发工具链随 CANN 统一发布，安装 CANN 即完成安装。由于算子编译环境依赖复杂，为避免环境问题影响学习体验，本教程要求使用 CANN 容器环境，不支持非容器化(裸机或虚拟机等)的环境。  

## 2. 创建工作区并下载代码仓库

创建 `workspace` 目录，用于存放示例执行过程中生成的各类文件；并将代码仓库克隆至 `~/ot_demo` 目录，克隆完成后，示例路径为 `~/ot_demo/msot/example`：

```shell
mkdir -p ~/ot_demo/workspace
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

若环境中 `git` 下载异常，可直接从 GitCode 网站下载仓库压缩包，手动上传至服务器，并确保目录结构与上述一致。

## 3. 设置芯片 SoC 型号信息

因芯片 SoC 型号信息在后续多条命令中频繁使用，此处统一获取并存入环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`，便于后续引用。

> [!CAUTION]注意   
> 环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 仅用于本次快速入门学习，商用开发请勿使用此变量。

请执行如下命令：

```shell
export MY_STUDY_VAR_CHIP_SOC_TYPE=$(python3 -c "import acl; print(acl.get_soc_name().replace('Ascend', ''))")
```
