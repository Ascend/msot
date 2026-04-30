# 算子开发工具链安装指南

<br>

## 1. 安装说明

MindStudio Operator Tools（msOT）是面向昇腾 AI 处理器的算子开发工具链，包含算子设计（msKPP）、算子工程（msOpGen）、异常检测（msSanitizer）、算子调试（msDebug）、算子调优（msOpProf）和算子调用（msKL）等工具。msOT工具安装完成后，其他子工具无需重复安装。

msOT工具的安装方式包括：

- 使用CANN包安装：msOT工具完整功能已集成在CANN包中，请参考《[CANN 快速安装](https://www.hiascend.com/cann/download)》安装昇腾NPU驱动和CANN软件（包含Toolkit和ops包），并配置环境变量。
- 源码编译安装：如需使用最新代码的功能，或对源码进行修改以增强功能，可下载本仓库代码，自行编译、打包工具并完成安装，具体请参见[源码编译安装](#2-源码编译安装)。

## 2. 源码编译安装

如需使用最新代码的功能，可下载本仓库代码，自行编译、打包并完成安装。

### 2.1 编译环境准备

请按照以下文档进行环境配置：《[算子工具开发环境安装指导](../common/dev_env_setup.md)》。

若为root用户，则执行以下命令进行依赖安装：

- OpenEuler环境：

    ```sh
    yum install git-lfs
    ```

- Ubuntu环境：

    ```sh
    apt-get install git-lfs
    ```
    
若为非root用户，则执行以下命令进行依赖安装：

- OpenEuler环境：

    ```sh
    sudo yum install git-lfs
    ```

- Ubuntu环境：

    ```sh
    sudo apt-get install git-lfs
    ```       

### 2.2 克隆本仓库

```shell
cd ~
git clone https://gitcode.com/Ascend/msot.git
```

### 2.3 执行编译打包

通过一键式脚本自动完成依赖仓库的下载与构建流程（首次耗时约 15 分钟）：

```shell
cd msot
python3 build.py
```

提示类似如下信息则表示构建成功：

```text
Self-extractable archive "ascend-mindstudio-operator-tools_1.0.0_aarch64.run" successfully created.
[100%] Built target package_msot
```

### 2.4 安装

#### 2.4.1 准备 run 包

run 包将生成在 `output` 目录下，执行以下命令为其添加可执行权限：

```shell
cd output
chmod +x ascend-mindstudio-operator-tools_*.run
```

#### 2.4.2 安装

将 run 包拷贝到运行环境中（本机安装则无需拷贝），执行如下安装命令：

```shell
./ascend-mindstudio-operator-tools_*.run --run
```

安装过程中，若环境中已有旧版工具，会提示是否替换：输入 `y` 并回车即可执行覆盖安装。    
若输出类似以下信息，则表明安装成功：

```text
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: all subpackage installed succeed
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: InstallPath: /usr/local/Ascend/cann-xxx
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: mindstudio-operator-tools package install success! The new version takes effect immediately.
```

> [!NOTE] 
> 
> 安装路径说明
> 
> 安装路径按以下优先级确定（从高到低）：
>
> 1. 命令行指定 `--install-path`：安装至指定目录（建议使用绝对路径）
>
>    ```shell
>    ./ascend-mindstudio-operator-tools_xxx.run --install-path=/opt/ascend --run
>    ```
>
> 2. 环境变量 `ASCEND_HOME_PATH` 已设置：安装至 `$ASCEND_HOME_PATH` 目录
> 3. 以上均未指定：默认安装至 `$HOME/Ascend` 目录

### 2.5 卸载

可通过以下命令卸载：

```shell
./ascend-mindstudio-operator-tools_*.run --uninstall
```

若输出类似以下信息，则表明卸载成功：

```text
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: all subpackage uninstalled succeed
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: mindstudio-operator-tools uninstall success!
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: End Time: 2026-03-02 12:18:24
```

> [!NOTE] 
> 
> 卸载路径说明
> 
> 默认将在 `$HOME/Ascend` 目录下卸载。若安装时通过 `--install-path` 指定了自定义路径，
> 则卸载时也需指定相同的路径，例如：
>
> ```shell
> ./ascend-mindstudio-operator-tools_xxx.run --install-path=/opt/ascend --uninstall
> ```

#### 2.6 升级

升级操作等同于覆盖安装：使用新版本的 run 包执行 [2.4.2 安装](#242-安装) 中的安装命令即可，安装程序会自动处理旧版本的替换。

## 3. FAQ

### 安装完成后，执行命令时未调用新编译的工具

请检查并配置以下环境变量，确保系统优先使用新安装的工具：

```shell
export ASCEND_HOME_PATH=$HOME/Ascend
export PATH=$ASCEND_HOME_PATH/bin:$PATH
export LD_LIBRARY_PATH=$ASCEND_HOME_PATH/lib64:$LD_LIBRARY_PATH
```

若使用了 `--install-path` 指定了自定义路径，请将 `$HOME/Ascend` 替换为对应的安装路径。

### run包已删除时如何卸载

可通过安装目录下的卸载脚本执行卸载：

```shell
bash $HOME/Ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```

若安装时使用了 `--install-path` 指定了自定义路径（如 `/opt/ascend`），请使用该路径下的卸载脚本：

```shell
bash /opt/ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```
