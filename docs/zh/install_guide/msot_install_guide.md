# 算子开发工具链安装指南

<br>

## 1. 安装说明

本工具链已集成于CANN中，若已安装 CANN 且无需更新此工具，可直接使用，无需按本文档安装。

若您的环境尚未安装 CANN，请参见《[CANN 快速安装](https://www.hiascend.com/cann/download)》安装昇腾NPU驱动和 CANN 软件（包含 Toolkit 和 ops 包），并配置环境变量。

如需单独升级本工具或使用最新版本，您可通过以下三种方式进行安装：[在线安装](#21-在线安装)、[离线安装](#22-离线安装)、[源码安装](#23-源码安装)。

## 2. 安装方式

### 2.1 在线安装

若您的设备具备互联网访问能力，可通过一条命令完成单个工具的下载与安装，可自由选择部分或全部安装。请参见昇腾社区MindStudio[下载](https://www.hiascend.com/developer/software/mindstudio/download)页面，选择对应的CANN版本，使用场景选择“算子开发”，并在安装方式中选择“在线安装”，系统将引导您完成后续操作。

### 2.2 离线安装

对处于企业内网等无外网环境的设备，请先在可联网的机器上下载完整的离线安装包，再将其传输至目标设备进行安装。请参见昇腾社区MindStudio[下载](https://www.hiascend.com/developer/software/mindstudio/download)页面，选择对应的CANN版本，使用场景选择“算子开发”，并在安装方式中选择“离线安装”，获取对应的安装包及操作指引。

### 2.3 源码安装

如需使用最新代码的功能，可下载本仓库代码，自行编译、打包并完成算子工具链安装。

#### 2.3.1 编译环境准备

源码编译统一使用 MindStudio 标准构建环境。

- 日常开发或使用已发布镜像，请参考《[MindStudio 工具开发环境安装指导](../common/dev_env_setup.md)》。
- 需要从基础操作系统复现环境、执行源码构建验证或单元测试验证时，必须参考《[MindStudio 统一构建镜像制作指南](../common/docker_image_build_guide.md)》，从 openEuler 基础镜像现场构建环境镜像。

本文档后续的源码编译和单元测试命令，均在上述指定镜像容器或现场构建的环境镜像的容器中执行，CANN 软件包版本、GCC 版本和 Python 版本以统一镜像制作指南为准。

镜像构建完成后，必须使用统一镜像制作指南第 7 章给出的 `ctr_in.py` 命令，在交互式终端中启动并进入容器。不得使用普通 `docker run` 创建容器，也不得使用 `docker exec <容器名> bash -c '<命令>'` 替代交互式环境；否则可能跳过 Python、GCC 和 CANN 环境初始化。

进入 `ctr_in.py` 打开的容器的交互式 Shell 后，执行如下命令克隆本仓库：

```bash
cd ~
git clone https://gitcode.com/Ascend/msot.git
```

#### 2.3.2 执行编译

保持在 `ctr_in.py` 打开的同一个交互式容器的 Shell 中，执行以下命令，自动完成依赖下载与构建：

```bash
cd ~/msot
python3 build.py
```

构建成功后，run 包将生成在 `artifacts/` 目录下。

#### 2.3.3 执行单元测试（可选）

此步骤非安装必需。如需验证代码基本功能，可执行单元测试：

```bash
cd ~/msot
python3 build.py test
```

命令返回码为 0，且测试用例均无失败，表示单元测试通过。

#### 2.3.4 安装

##### 2.3.4.1 准备 run 包

run 包将生成在 `artifacts` 目录下，执行以下命令为其添加可执行权限：

```bash
cd artifacts
chmod +x ascend-mindstudio-operator-tools_*.run
```

##### 2.3.4.2 安装

将 run 包拷贝到运行环境中（本机安装则无需拷贝），执行如下安装命令：

```bash
./ascend-mindstudio-operator-tools_*.run --install
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
> **安装路径说明**
> 
> 安装路径按以下优先级确定（从高到低）：
>
> 1. 命令行指定 `--install-path`：安装至指定目录（建议使用绝对路径）
>
>    ```bash
>    ./ascend-mindstudio-operator-tools_xxx.run --install --install-path=/opt/ascend
>    ```
>
> 2. 环境变量 `ASCEND_HOME_PATH` 已设置：安装至 `$ASCEND_HOME_PATH` 目录
> 3. 以上均未指定：默认安装至 `$HOME/Ascend` 目录

#### 2.3.5 卸载

可通过以下命令卸载：

```bash
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
> ```bash
> ./ascend-mindstudio-operator-tools_xxx.run --install-path=/opt/ascend --uninstall
> ```

#### 2.3.6 升级

升级操作等同于覆盖安装：按上述安装步骤执行即可，安装程序会自动处理旧版本的替换。

## 3. FAQ

### 3.1 安装完成后，执行命令时未调用新编译的工具

请检查并配置以下环境变量，确保系统优先使用新安装的工具：

```bash
export ASCEND_HOME_PATH=$HOME/Ascend
export PATH=$ASCEND_HOME_PATH/bin:$PATH
export LD_LIBRARY_PATH=$ASCEND_HOME_PATH/lib64:$LD_LIBRARY_PATH
```

若使用了 `--install-path` 指定了自定义路径，请将 `$HOME/Ascend` 替换为对应的安装路径。

### 3.2 run 包已删除时如何卸载

可通过安装目录下的卸载脚本执行卸载：

```bash
bash $HOME/Ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```

若安装时使用了 `--install-path` 指定了自定义路径（如 `/opt/ascend`），请使用该路径下的卸载脚本：

```bash
bash /opt/ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```
