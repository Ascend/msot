# MindStudio Operator Tools Installation Guide

<br>

## 1. Installation Notes

This toolchain is integrated into CANN. If CANN is already installed and you do not need to update this tool, you can use it directly without installing it as described in this document.

If CANN is not yet installed in your environment, refer to [CANN Quick Installation](https://www.hiascend.com/cann/download) to install the Ascend NPU driver and CANN software (including the Toolkit and ops packages), and configure the environment variables.

If you need to upgrade this tool separately or use the latest version, you can install it using any of the following methods: [online installation](#21-online-installation), [offline installation](#22-offline-installation), or [source code installation](#23-source-code-installation).

## 2. Installation Methods

### 2.1 Online Installation

If your device has internet access, you can complete the download and installation of a single tool with one command, and you can freely choose to install some or all of the tools. Refer to the MindStudio [download](https://www.hiascend.com/developer/software/mindstudio/download) page on the Ascend community website, select the corresponding CANN version, select "Operator Development" as the usage scenario, and select "Online Installation" as the installation method. The system will guide you through the subsequent operations.

### 2.2 Offline Installation

For devices in an environment without internet access, such as an enterprise intranet, first download the complete offline installation package on a machine with internet access, and then transfer it to the target device for installation. Refer to the MindStudio [download](https://www.hiascend.com/developer/software/mindstudio/download) page on the Ascend community website, select the corresponding CANN version, select "Operator Development" as the usage scenario, and select "Offline Installation" as the installation method to obtain the corresponding installation package and operation guide.

### 2.3 Source Code Installation

If you need to use the features of the latest code, you can download the code from this repository, compile, package, and install the operator toolchain yourself.

#### 2.3.1 Preparing the Compilation Environment

Configure the environment by referring to the following document: [Operator Tool Development Environment Setup Guide](../common/dev_env_setup.md).

#### 2.3.2 Cloning the Repository

```bash
cd ~
git clone https://gitcode.com/Ascend/msot.git -b 26.1.0
```

#### 2.3.3 Compilation and Packaging

Use the one-click script to automatically complete the download and build process of dependency repositories (takes about 20 minutes for the first time):

```bash
cd msot
python3 build.py
```

A message similar to the following indicates a successful build:

```text
Self-extractable archive "ascend-mindstudio-operator-tools_1.0.0_aarch64.run" successfully created.
[100%] Built target package_msot
```

#### 2.3.4 Installation

##### 2.3.4.1 Preparing the Run Package

The run package will be generated in the `output` directory. Run the following command to add executable permissions to it:

```bash
cd output
chmod +x ascend-mindstudio-operator-tools_*.run
```

##### 2.3.4.2 Installation

Copy the run package to the runtime environment (copying is not required for local installation), and run the following installation command:

```bash
./ascend-mindstudio-operator-tools_*.run --install
```

During installation, if an older version of the tool already exists in the environment, you will be prompted to replace it: enter `y` and press Enter to perform an overwrite installation.  
If output similar to the following is displayed, the installation is successful:

```text
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: all subpackage installed succeed
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: InstallPath: /usr/local/Ascend/cann-xxx
[mindstudio-operator-tools] [2026-03-02 12:16:42] [INFO]: mindstudio-operator-tools package install success! The new version takes effect immediately.
```

> [!NOTE] 
> 
> **Installation Path Description**
> 
> The installation path is determined by the following priorities (from highest to lowest):
>
> 1. `--install-path` specified on the CLI: installs to the specified directory (absolute path recommended).
>
>    ```bash
>    ./ascend-mindstudio-operator-tools_xxx.run --install --install-path=/opt/ascend
>    ```
>
> 2. Environment variable `ASCEND_HOME_PATH` is set: installs to the `$ASCEND_HOME_PATH` directory.
> 3. None of the above: installs to the `$HOME/Ascend` directory by default.

#### 2.3.5 Uninstallation

You can uninstall it using the following command:

```bash
./ascend-mindstudio-operator-tools_*.run --uninstall
```

If the output is similar to the following, the uninstallation is successful:

```text
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: all subpackage uninstalled succeed
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: mindstudio-operator-tools uninstall success!
[mindstudio-operator-tools] [2026-03-02 12:18:24] [INFO]: End Time: 2026-03-02 12:18:24
```

> [!NOTE] 
> 
> Uninstallation Path Description
> 
> By default, it will be uninstalled from the `$HOME/Ascend` directory. If a custom path was specified using `--install-path` during installation,
> the same path must also be specified during uninstallation, for example:
>
> ```bash
> ./ascend-mindstudio-operator-tools_xxx.run --install-path=/opt/ascend --uninstall
> ```

#### 2.3.6 Upgrade

The upgrade operation is equivalent to an overwrite installation: simply follow the preceding installation steps, and the installer will automatically handle the replacement of the old version.

## 3. FAQ

### 3.1 After Installation, the Newly Compiled Tool Is Not Invoked When Executing Commands

Check and configure the following environment variables to ensure the system prioritizes the newly installed tools:

```bash
export ASCEND_HOME_PATH=$HOME/Ascend
export PATH=$ASCEND_HOME_PATH/bin:$PATH
export LD_LIBRARY_PATH=$ASCEND_HOME_PATH/lib64:$LD_LIBRARY_PATH
```

If `--install-path` is used to specify a custom path, replace `$HOME/Ascend` with the corresponding installation path.

### 3.2 How to Uninstall When the RUN Package Has Been Deleted

You can perform the uninstallation by using the uninstall script in the installation directory:

```bash
bash $HOME/Ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```

If `--install-path` was used to specify a custom path (such as `/opt/ascend`) during installation, use the uninstall script under that path:

```bash
bash /opt/ascend/share/info/mindstudio-operator-tools/script/uninstall.sh
```
