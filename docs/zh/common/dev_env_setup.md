# 算子工具开发环境安装指导

<br>

## 1. 拉取镜像

> [!NOTE] 关于编译环境的说明    
> 由于 glibc 遵循“向后兼容”但不“向前兼容”的原则，为确保编译生成的可执行程序能在大多数操作系统上运行，编译镜像通常选用较旧版本的操作系统。  
> 若在较高版本操作系统上编译的程序发布到较低版本环境中运行，可能出现异常。场景二的编译专用镜像发布于 2018 年左右，可广泛适配当前主流的老旧运行环境。    
> 但该操作系统版本功能较为受限（例如不支持 VS Code 远程连接），因此仅建议用于最终编译打包；日常开发与调试请使用较新镜像，以提升效率与体验。

### 场景选择指南

对于只需在单一且无须考虑跨操作系统版本兼容性的环境中进行编译和运行的情况，推荐采用**场景一**，以实现最高开发效率。    
反之，如果需要将编译后的软件包部署到旧版操作系统，则应选择**场景二**。（建议首先使用场景一中的镜像完成软件的调试工作，确保其稳定性后再切换至场景二的镜像进行最终编译，以此达到开发效率与运行兼容性的平衡。）

### 场景一：单一环境下的开发与调试

请使用 CANN 官方容器镜像作为编译环境，镜像详情可参见<a href="https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884" target="_blank">《CANN 官方镜像仓库》</a>。   
请选用类似以下版本的 `openEuler` 镜像：`8.5.0-xxx-openeuler24.03-py3.11`（其中 xxx 需根据您的昇腾 AI 处理器型号填写）。   
以昇腾 910B 为例，拉取命令如下：

```shell
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.0-910b-openeuler24.03-py3.11
```

### 场景二：针对老旧操作系统的打包与部署

请依据您的具体环境，从华为云官方容器镜像仓库获取相应的算子开发编译专用 Docker 镜像。

- **x86 架构**：

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:x86_20260211_v01
```

- **arm 架构**：

```shell
docker pull swr.cn-north-4.myhuaweicloud.com/mindstudio-image/msot:arm_20260211_v01
```

## 2. 启动容器

请参见<a href="https://gitcode.com/mengguangxin/ascend_op_docker/blob/main/cann_docker_env_install.md#2--启动容器" target="_blank">《CANN 容器环境安装指南 > 第二节》</a>完成容器的启动。

## 3. 环境设置

### 3.1. 场景一的环境配置

进入容器后，执行如下命令：

```shell
yum install ninja-build -y
yum install pigz -y
```

### 3.2 场景二的环境配置

执行以下命令，将 CANN 环境变量配置写入 `~/.bashrc` 文件，以确保其永久生效：

```shell
echo "source /usr/local/Ascend/cann/set_env.sh" >> ~/.bashrc
source ~/.bashrc
```

## 4. FAQ

### 4.1 下载依赖时多次提示输入密码，如何仅输入一次？

可通过以下命令配置并保存 Git 凭证：

```shell
git config --global credential.helper store
```
