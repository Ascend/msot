# MindStudio Operator Tools 安装指南

<br>

## 1. 二进制安装
MindStudio 工具链已集成在 CANN 包中发布，可通过以下方式完成安装： 

### 方式一：依据 CANN 官方文档安装  
请参考<a href="https://www.hiascend.com/document/detail/zh/canncommercial/850/softwareinst" target="_blank">《CANN 安装官方文档》</a>，
按文档逐步完成安装与配置。

### 方式二：使用 CANN 官方容器镜像   
请访问<a href="https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884" target="_blank">《CANN 官方镜像仓库》</a>，
按仓库中的指引完成镜像拉取及容器启动。

<br>

## 2. 源码安装
如需使用最新代码的功能，可下载本仓库代码，自行编译、打包并完成安装：

### 2.1 编译环境准备
请按照以下文档进行环境配置：[《算子工具开发环境安装指导》](../common/dev_env_setup.md)。

### 2.2 执行编译打包
通过一键式脚本自动完成依赖仓库的下载与构建流程（耗时约15分钟）：
```
python build.py
```

### 2.3 安装与卸载

#### 2.3.1 准备run包
run 包将生成在 `output` 目录下，执行以下命令为其添加可执行权限：
```
cd output
chmod +x ascend-mindstudio-operator-tools_*.run
```

#### 2.3.2 安装
将 run 包拷贝到运行环境中（本机安装则无需拷贝），执行如下安装命令：
```
./ascend-mindstudio-operator-tools_*.run --run
```
安装过程中，若环境中已有旧版工具，会提示是否替换：输入 `y` 并回车即可执行覆盖安装。
>[!NOTE] 安装路径说明   
> 若环境中已配置 `ASCEND_HOME_PATH` 环境变量，工具将安装至 `$ASCEND_HOME_PATH` 目录；
> 否则，默认安装至 `$HOME/Ascend` 目录；  
> 如需指定自定义安装路径，请使用 `--install-path` 选项，例如：
> `./ascend-mindstudio-operator-tools_*.run --install-path=./xxx --run`，即可将该运行包安装至 `xxx` 目录。

#### 2.3.3 卸载
可通过以下命令卸载：
```
./ascend-mindstudio-operator-tools_*.run --uninstall
```
>[!NOTE] 卸载路径说明   
> 默认将在 `$HOME/Ascend` 目录下卸载；若先前安装时通过 `--install-path` 指定了自定义路径，
> 则卸载时也需显式添加 `--install-path` 选项，例如：
> `./ascend-mindstudio-operator-tools_*.run --install-path=./xxx --uninstall`。

#### 2.3.4 升级
升级操作本质上是卸载旧版本并安装新版本，与[2.3.2 安装](#232-安装)中所述的覆盖安装方式一致，请参见相关操作说明。

### 2.4 FAQ
#### 2.4.1 安装完成后，执行命令时未调用新编译的工具
请按以下方式检查并配置环境变量，确保系统优先使用新安装的算子工具：
```
export ASCEND_HOME_PATH=$HOME/Ascend  # 或 export ASCEND_HOME_PATH=$PWD/xxx（指定路径安装场景）
export PATH=$ASCEND_HOME_PATH/bin:$PATH
export LD_LIBRARY_PATH=$ASCEND_HOME_PATH/lib64:$LD_LIBRARY_PATH
```

#### 2.4.2 run 包已删除时如何卸载？
可通过以下命令执行卸载：
```
bash $HOME/Ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```
若为指定路径安装，请使用该路径下的卸载脚本：
```
bash ./xxx/share/info/mindstudio-operator-tools/script/uninstall.sh 
```