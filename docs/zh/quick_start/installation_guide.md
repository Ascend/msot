# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

>[!CAUTION]注意   
>**免责声明**   
>本文档及相关脚本仅供学习使用，不承诺生产环境的稳定性和安全性，使用者需自行评估风险并承担相应责任。

## 1. 算子工具学习环境安装

您需要准备一台 Linux 服务器，配备至少 1 张昇腾 NPU 卡，且已安装好 NPU 驱动和固件。

### 1.1 算子工具安装

算子工具是集成到 CANN 中发布的，提供以下两种安装方式：

1. **容器化运行环境**：推荐方式，Docker 服务正常时 5 分钟内即可完成，请参考[《CANN容器环境安装指南》](./cann_container_setup.md)进行安装；
2. **裸机或虚机环境**：安装复杂，耗时较长，多用户共享易引发冲突，可能遇到难以解决的环境问题。如确需使用此类环境，请参考<a href="https://www.hiascend.com/cann/download" target="_blank">《CANN 官方安装指南》</a>进行安装，版本使用较新的即可。

### 1.2 工作区目录初始化

**1. 创建工作区**   
创建 `workspace` 目录，用于存放示例执行过程中生成的各类文件，路径为`~/ot_demo/workspace`（其中 “ot” 为 Operator Tool 算子工具的首字母缩写）：

```shell
mkdir -p ~/ot_demo/workspace
```

**2. 下载仓库**   
下载至目录 `~/ot_demo`，下载后示例路径为 `~/ot_demo/msot/example`：

```shell
git clone https://gitcode.com/Ascend/msot.git ~/ot_demo/msot
```

> 提示：如果环境中 git 下载异常，可以直接从 gitcode.com 下载压缩包，手动传到服务器上，保持目录结构正确即可。

### 1.3 芯片 SoC 型号获取

因芯片 SoC 型号在后续多条命令中频繁使用，且获取方式较复杂，此处统一获取并存入环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`，便于后续引用。

>[!CAUTION]注意   
>环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 仅用于本次快速入门学习，商用开发请勿使用此变量。

#### 1.3.1 自动获取芯片 SoC 型号

如想快速体验工具，可运行以下命令自动获取并设置芯片 SoC 型号：

```shell
python3 ~/ot_demo/msot/example/quick_start/public/get_ai_soc_version.py
```

若执行成功，按提示运行：

```shell
source set_chip_env_var.sh
```

该脚本将芯片 SoC 型号（去除“Ascend”前缀，如 910B4、910_9392）写入环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE`。

#### 1.3.2 手动获取芯片 SoC 型号

如想学习芯片 SoC 型号的概念及获取方法，请参考[《昇腾芯片 SoC 型号获取方法》](get_chip_soc_type.md)手动获取芯片 SoC 型号，并将去除 "Ascend" 前缀后的值（如 910B4）替换以下命令中的 `<YOUR_CHIP_NAME>` 后执行：

```shell
echo "export MY_STUDY_VAR_CHIP_SOC_TYPE=<YOUR_CHIP_NAME>" >> ~/.bashrc && source ~/.bashrc
```

>[!CAUTION]注意    
>`MY_STUDY_VAR_CHIP_SOC_TYPE` 的值为去掉 Ascend 前缀后的值：   
>正确值：910B4、910_9392；  
>错误值：Ascend910B4、Ascend910_9392。

### 1.4 安装 Python 库

算子工程构建依赖以下库，请执行如下命令安装：

```shell
pip3 install -r ~/ot_demo/msot/example/quick_start/public/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ln -sf /usr/local/bin/python3 /usr/bin/python3
```

>[!NOTE]说明   
>由于官网下载速度较慢，上述命令使用了阿里源进行安装。若您的环境无法访问阿里源，或出于安全考虑不信任该源，可移除 -i xxx 参数以恢复默认源。
