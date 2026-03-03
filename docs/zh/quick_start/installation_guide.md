# 昇腾 AI 算子开发工具链学习环境安装指南

<br>

>[!CAUTION]注意   
>**免责声明**   
>本文档及相关脚本仅供学习使用，不承诺生产环境的稳定性和安全性，使用者需自行评估风险并承担相应责任。

## 1. 算子工具学习环境安装

您需要准备一台 Linux 服务器，配备至少 1 张昇腾 NPU 卡，且已安装好 NPU 驱动和固件。

### 1.1 算子工具安装

建议使用如下第 1 种方案的 CANN 容器环境进行体验，裸机/虚机安装较复杂，多人使用易冲突，且可能遇到不易解决的环境问题：   

1. CANN 容器环境（基于社区经验总结的快速指导）：请参考<a href="https://gitcode.com/mengguangxin/ascend_op_docker/blob/main/cann_docker_env_install.md" target="_blank">《CANN容器环境安装指南》</a>安装，在 Docker 服务正常的情况下可在 5 分钟内完成；   
2. CANN 容器环境（基于华为官方镜像仓网站指导）：如果担心第 1 种方案的安全问题，请访问<a href="https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884" target="_blank">《CANN官方镜像仓库》</a>，按仓库中的指导自主探索完成安装；
3. 裸机/虚机环境：如必须使用此类环境，请参考<a href="https://www.hiascend.com/document/detail/zh/canncommercial/83RC1/softwareinst/instg/instg_0008.html?Mode=PmIns&InstallType=local&OS=openEuler&Software=cannToolKit" target="_blank">《CANN安装官方文档》</a>安装，版本使用较新的即可。

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
