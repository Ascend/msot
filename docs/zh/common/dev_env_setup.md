# 算子工具开发环境安装指导

<br>

## 1. 拉取镜像
请使用 CANN 官方容器镜像作为编译环境，镜像详情可参见<a href="https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884" target="_blank">《CANN 官方镜像仓库》</a>。   
编译主线最新代码，请选用以下版本的镜像：`8.5.0-xxx-openeuler24.03-py3.11`（其中 xxx 需根据您的昇腾 AI 处理器型号填写）。   
以昇腾 910B 为例，拉取命令如下：
```shell
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.0-910b-openeuler24.03-py3.11
```

## 2. 容器启动
建议使用如下第 1 种方案：   
1. 基于社区经验总结的快速指导：1分钟启动容器，请参见<a href="https://gitcode.com/mengguangxin/ascend_op_docker/blob/main/cann_docker_env_install.md#2--启动容器" target="_blank">《CANN容器环境安装指南 > 第二节》</a>
2. 基于华为官方镜像仓网站指导：如果担心第 1 种方案的安全问题，请参见<a href="https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884" target="_blank">《CANN 官方镜像仓库》</a>, 按仓库中的指导自主探索完成启动；

## 3. 安装编译工具
进入容器后，执行如下命令：
```shell
yum install ninja-build -y
yum install pigz -y
```

## 4. FAQ
### 4.1 下载依赖时多次提示输入密码，怎么能只输出一次？
可通过以下命令配置并保存 Git 凭证：   
```shell
git config --global credential.helper store
```
### 4.2 按官方镜像仓网站指导启动容器为什么clone代码失败，提示网络异常？
Ascend 环境通常涉及复杂的驱动映射（如 /dev/davinci 等）。在 Docker 启动时，驱动程序与硬件通信有时需要特定的内存访问权限
（如 CAP_SYS_ADMIN 或 CAP_IPC_LOCK）。如果没有这些权限，底层的通信库可能会在初始化网络栈或系统调用时发生崩溃或阻塞，
表现出来的现象就是网络请求失败，解决方法如下：   
命令参数增加如下，再重新启动：
```shell
    --cap-add SYS_ADMIN \
    --cap-add NET_ADMIN \
    --security-opt seccomp=unconfined \
```
如果还是不行，因只是编译对容器运行安全要求较低，可以增加如下参数开启特权模式：
```shell
   --privileged=true \
```