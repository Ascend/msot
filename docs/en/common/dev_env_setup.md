# Operator Tool Development Environment Setup Guide

<br>

## 1. Pulling the Image

> [!NOTE] Notes on the Build Environment
> Since glibc follows the principle of "backward compatibility" but not "forward compatibility", to ensure that the compiled executable programs can run on most operating systems, the build image typically uses an earlier version of the operating system.  
> If a program compiled on a higher version operating system is deployed to a lower version environment, exceptions may occur. The dedicated build image for Scenario 2 was released around 2018 and can be widely adapted to current mainstream legacy runtime environments.
> However, this operating system version has relatively limited functionality (for example, it does not support VS Code remote connections), so it is only recommended for final compilation and packaging; please use a newer image for daily development and debugging to improve efficiency and experience.

### Scenario Selection Guide

For scenarios where compilation and execution only need to occur in a single environment without considering cross-OS version compatibility, **Scenario 1** is recommended to achieve the highest development efficiency.  
Conversely, if the compiled software package needs to be deployed to an older operating system, **Scenario 2** should be selected. (It is recommended that you first use the image from Scenario 1 to complete software debugging, ensuring its stability before switching to the Scenario 2 image for the final compilation, thereby balancing development efficiency and runtime compatibility.)

### Scenario 1: Development and Debugging in a Single Environment

Please use the official CANN container image as the compilation environment. For image details, refer to [CANN Official Image Repository](https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884).  
Please select an `openEuler` image with a version similar to: `8.5.0-xxx-openeuler24.03-py3.11` (where xxx needs to be filled in according to your Ascend AI processor model).  
Taking Atlas A2 Training Series/Atlas A2 Inference Series as an example, the pull command is as follows:

```shell
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.0-910b-openeuler24.03-py3.11
```

### Scenario 2: Packaging and Deployment for Legacy Operating Systems

Please obtain the corresponding operator development and compilation-specific Docker image from the Huawei Cloud official container image repository based on your specific environment.

- **x86 architecture**:

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:x86_20260211_v01
```

- **Arm architecture**:

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:arm_20260211_v01
```

## 2. Starting the Container

Refer to [CANN Container Environment Installation Guide > Section 2](../quick_start/cann_container_setup.md#2-starting-the-container) to start the container.

## 3. Environment Setup

### 3.1. Environment Configuration for Scenario 1

After entering the container, run the following command:

```shell
yum install ninja-build -y
yum install pigz -y
```

### 3.2 Environment Configuration for Scenario 2

Run the following command to write the CANN environment variable configuration to the `~/.bashrc` file to ensure it takes effect permanently:

```shell
echo "source /usr/local/Ascend/cann/set_env.sh" >> ~/.bashrc
source ~/.bashrc
```

## 4. FAQ

### 4.1 When downloading dependencies, I am prompted to enter my password multiple times. How can I enter it only once?

You can configure and save Git credentials using the following command:

```shell
git config --global credential.helper store
```
