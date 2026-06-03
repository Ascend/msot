# MindStudio Operator Tools Installation Guide

<br>

MindStudio Operator Tools (msOT) is an operator development toolchain for Ascend AI processors, providing tools such as performance prediction (msKPP), project generation (msOpGen), anomaly detection (msSanitizer), native debugging (msDebug), performance analysis (msOpProf), and quick invocation (msKL).

This document primarily introduces the installation, uninstallation, and upgrade methods for msOT tools. The installation methods are divided into two types: **binary installation** and **source code installation**.

<br>

## 1. Binary Installation

The MindStudio toolchain is integrated and released within the CANN package. You can complete the installation using the following methods:

### Method 1: Installing by Referring to the Official CANN Documentation

Refer to the *[CANN Official Installation Guide](https://www.hiascend.com/cann/download)* and follow the documentation to complete the installation and configuration step by step.

### Method 2: Using the Official CANN Container Image

Visit the [CANN Official Image Repository](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884) and follow the instructions in the repository to pull the image and start the container.

<br>

## 2. Source Code Installation

If you need to use the features of the latest code, you can download the code from this repository, compile, package, and install it yourself.

### 2.1 Preparing the Compilation Environment

Configure the environment by referring to the following document: *[Operator Tool Development Environment Setup Guide](../common/dev_env_setup.md)*.

### 2.2 Cloning the Repository

```shell
cd ~
git clone https://gitcode.com/Ascend/msot.git
```

### 2.3 Compilation and Packaging

Use the one-click script to automatically complete the download and build process of dependency repositories (takes about 15 minutes for the first time):

```shell
cd msot
python3 build.py
```

A message similar to the following indicates a successful build:

```text
Self-extractable archive "ascend-mindstudio-operator-tools_1.0.0_aarch64.run" successfully created.
[100%] Built target package_msot
```

### 2.4 Installation and Uninstallation

#### 2.4.1 Preparing the Run Package

The run package will be generated in the `output` directory. Run the following command to add executable permissions to it:

```shell
cd output
chmod +x ascend-mindstudio-operator-tools_*.run
```

#### 2.4.2 Installation

Copy the run package to the runtime environment (copying is not required for local installation), and run the following installation command:

```shell
./ascend-mindstudio-operator-tools_*.run --run
```

During installation, if an older version of the tool already exists in the environment, you will be prompted to replace it: enter `y` and press Enter to perform an overwrite installation.  
If output similar to the following is displayed, the installation is successful:

```text
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: all subpackage installed succeed
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: InstallPath: /usr/local/Ascend/cann-xxx
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: mindstudio-operator-tools package install success! The new version takes effect immediately.
```

> [!NOTE] Installation Path Description
> The installation path is determined by the following priorities (from highest to lowest):
>
> 1. `--install-path` specified on the command line: installs to the specified directory (absolute path recommended)
>
>    ```shell
>    ./ascend-mindstudio-operator-tools_xxx.run --install-path=/opt/ascend --run
>    ```
>
> 2. Environment variable `ASCEND_HOME_PATH` is set: installs to the `$ASCEND_HOME_PATH` directory
> 3. None of the above: Installed to the `$HOME/Ascend` directory by default

#### 2.4.3 Uninstallation

You can uninstall it using the following command:

```shell
./ascend-mindstudio-operator-tools_*.run --uninstall
```

If the output is similar to the following, the uninstallation is successful:

```text
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: all subpackage uninstalled succeed
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: mindstudio-operator-tools uninstall success!
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: End Time: 2026-03-02 12:18:24
```

> [!NOTE] Uninstallation Path Description
> By default, it will be uninstalled from the `$HOME/Ascend` directory. If a custom path was specified using `--install-path` during installation,
> the same path must also be specified during uninstallation, for example:
>
> ```shell
> ./ascend-mindstudio-operator-tools_xxx.run --install-path=/opt/ascend --uninstall
> ```

#### 2.4.4 Upgrade

The upgrade operation is equivalent to an overwrite installation: run the installation command from [2.4.2 Installation](#242-installation) using the new version of the run package, and the installer will automatically handle the replacement of the old version.

## 3. FAQ

### After installation, the newly compiled tool is not invoked when executing commands

Check and configure the following environment variables to ensure the system prioritizes the newly installed tools:

```shell
export ASCEND_HOME_PATH=$HOME/Ascend
export PATH=$ASCEND_HOME_PATH/bin:$PATH
export LD_LIBRARY_PATH=$ASCEND_HOME_PATH/lib64:$LD_LIBRARY_PATH
```

If `--install-path` is used to specify a custom path, replace `$HOME/Ascend` with the corresponding installation path.

### How to Uninstall When the RUN Package Has Been Deleted

You can perform the uninstallation by using the uninstall script in the installation directory:

```shell
bash $HOME/Ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```

If `--install-path` was used to specify a custom path (such as `/opt/ascend`) during installation, use the uninstall script under that path:

```shell
bash /opt/ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```
