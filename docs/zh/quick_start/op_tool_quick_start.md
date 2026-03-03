# 算子开发工具链快速入门（核心流程 10 分钟体验）

<br>

## 1. 概述

MindStudio 算子开发工具链包含多种工具，本文档以开发一个简单加法算子为例，贯穿算子开发全流程，系统体验各工具的核心功能，帮助初学者直观感受这些工具为算子开发带来的高效与便捷。
<br>

### 1.1 前言

#### ▸ 预备知识

您需要掌握昇腾算子开发的基础知识，至少理解 <a href="https://www.hiascend.com/developer/blog/details/0239124507827469022" target="_blank">《昇腾 Ascend C 编程入门教程（纯干货）》</a> 里的内容，若已学习过 <a href="https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850/opdevg/Ascendcopdevg/atlas_ascendc_map_10_0002.html" target="_blank">《Ascend C 算子开发》</a> 则更佳。否则，可能难以充分理解本工具链各项功能的使用方法。

#### ▸ 学习目标

完成本教程后，您将掌握以下基础能力：使用 msKPP 对算子性能进行建模，自动生成 Ascend C 算子工程，调试并验证算子功能，检测算子中的内存越界、同步异常等运行时错误，分析算子性能瓶颈；同时，您将具备初步查阅各工具详细文档并快速上手中高级功能的技术基础。  

#### ▸ 学习耗时

“10 分钟” 指核心工具链的连续操作体验时间，不包含不可控的环境准备及工具原理学习时间。  
若您具备昇腾算子开发经验，采用容器安装方案或已具备环境，则可在 10 分钟内完成全流程体验。

| 章节 |       内容        |        实测纯操作时间        | 建议学习原理时间 |
|:--:|:----------------:|:---------------------:|:--------:|
| 1  |       环境准备       | 容器 ≤ 5 分，裸机/虚机 ≥ 20 分 |   5 分钟    |
| 2  |    设计 (msKPP)    |         30 秒          |   5 分钟    |
| 3  |   开发 (msOpGen)   |         1 分钟          |   20 分钟   |
| 4  | 检测 (msSanitizer) |         1 分钟          |   10 分钟   |
| 5  |   调试 (msDebug)   |         1 分钟          |   10 分钟   |
| 6  |  调优 (msOpProf)   |         1 分钟          |   10 分钟   |
| - |       时间总计       |  10 分钟 (容器方案或环境已具备)   |   60 分钟   |

> 注：操作时间基于环境已正确配置且无中断的前提。
>
#### ▸ 体验流程

1.环境准备(CANN) → 2.设计(msKPP) → 3.开发(msOpGen) → 4.检测(msSanitizer) → 5.调试(msDebug) → 6.调优(msOpProf)
> 关于体验顺序：1是基础，完成1后可体验2或3，4、5、6依赖于3，但彼此之间无依赖关系，可任意顺序进行或选择性跳过。

### 1.2 环境准备

请严格按照[《昇腾 AI 算子开发工具链学习环境安装指南》](installation_guide.md)完成环境安装与工作区配置。   
即使您已具备类似环境，也要按指南重新执行一遍，以确保所有依赖组件、环境变量等完整无缺。

环境安装完成后，从下一节起进入实际体验环节，全程支持 copy/paste 命令快速执行，若过程中出现报错，请参考[第 2.8 节 FAQ](#28-faq常见错误解决)进行排查与解决。

<br>

## 2. 操作步骤

### 2.1 【环境】运行环境预检

#### 2.1.1 验证环境变量配置

执行如下指令，确认系统输出正确的芯片 SoC 型号（如 910B4、910_9392）：   

```shell
echo $MY_STUDY_VAR_CHIP_SOC_TYPE
```

若该变量为空，请参照[第 1.2 节](#12-环境准备)进行正确设置。
>[!CAUTION]注意    
>请确保 MY_STUDY_VAR_CHIP_SOC_TYPE 环境变量已正确配置，否则后续步骤将频繁报错。此变量为学习环境专用，**正式商用版本中严禁使用**。

#### 2.1.2 确认 Python 插件已安装

执行以下命令，若输出"All is OK"，则表明所需 Python 包及其版本均满足规范：

```shell
python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
```

若报错，请参照[第 1.2 节](#12-环境准备)进行正确安装。

#### 2.1.3 确认代码仓正常

执行以下命令，若能正常列出目录内容，则说明代码仓已正确就位：

```shell
ls -al ~/ot_demo/msot/example/quick_start
```

若报错，请参照[第 1.2 节](#12-环境准备)完成正确的准备。

### 2.2 【设计】算子建模设计（msKPP）

首先，进行算子算法设计。借助 msKPP 工具，可在秒级时间内获得算子性能建模结果，在无硬件条件下预估性能，快速验证实现方案的可行性。先跟着操作体验效果，原理部分可稍后阅读：

>[!NOTE]说明   
> **知识点：msKPP 工具原理**   
> msKPP 并非传统可执行程序，而是一套专用于昇腾的 Python 类库。用户需通过import相关模块、编写并执行 Python 脚本，生成性能分析结果文件以完成建模。内部原理是预先采集真实环境中各类指令操作的性能数据，基于用户定义的算子执行流程，对各种性能开销进行建模与估算。

#### 2.2.1 编写 Python 建模脚本

**1. 创建子工作区目录**

```shell
mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
```

**2. 开发 Python 脚本**   
>[!NOTE]说明  
>**知识点（可选阅读）：msKPP 的 DSL 语言方案（Domain-Specific Language，领域特定语言）**   
>这套类库及接口是专为昇腾性能建模而设计的"方言"，需经过专门学习方可掌握，无法仅凭通用 Python 语法直接编写，但用法较简单，稍加学习即可应用。  
>常规开发流程：需先导入 Tensor、Chip 以及算子实现所必需的指令（例如 vadd），通过 with 语句进入算子实现代码的上下文，再创建 Tensor 以执行具体操作，样例脚本中已做了详细的注释，其他指令接口说明请参考<a href="https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/mskpp_api_reference.md" target="_blank">《msKPP 工具接口说明》</a>。

因是快速入门，将准备好的 msKPP 的 DSL 脚本复制到此即视为开发完成（本教程聚焦工具链使用，实际开发需自行实现）：

```shell
\cp -f ~/ot_demo/msot/example/quick_start/mskpp/mskpp_demo.py ./
```

#### 2.2.2 执行性能建模

执行 Python 脚本开始性能建模，如果成功，将自动在当前目录下生成 "MSKPP{timestamp}" 结果目录：

```shell
python3 mskpp_demo.py
```

如果脚本报错，提示 Chip is unsupported，请确认环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 是否正确设置，如变量为空，请参考[第 1.2 节](#12-环境准备)正确设置。

#### 2.2.3 查看建模结果

生成如下结果目录：

```text
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

以 Instruction_statistic.csv 为例，其内容如下：

| Instruction  | Duration(us) | Cycle | Size(B) | Ops  |
|:--------------:|:--------------:|:-------:|:---------:|:------:|
| MOV-GM_TO_UB |    0.3081    |  570  |  6144   |  -   |
|     VADD     |    0.0135    |  25   |    -    | 1536 |
| MOV-UB_TO_GM |    0.4254    |  787  |  3072   |  -   |

由上述内容可见，MOV_UB_TO_GM（从 UB 搬移到 GM）的耗时（Duration）最长，指令周期数（Cycle）也最多，是性能优化中需重点关注的关键路径。在实际开发中，如果发现此类内存搬运耗时占比过高，应优先考虑优化数据复用（Tiling）或使用更高效的搬运指令。

<br>

### 2.3 【开发】构建算子工程（msOpGen）

算法设计完成后，即可进入算子代码编写阶段。算子工程较为复杂且包含大量框架代码，msOpGen 工具可自动生成完整的算子工程框架，使开发者聚焦于核心算法实现，避免在项目搭建、编译配置等重复性工作上耗费时间。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.3.1 生成工程框架

**1. 创建子工作区目录**   
创建名为 `src` 的子目录，作为算子源码根目录，后续所有源码操作均基于此路径开展：

```shell
mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src/
```

**2. 开发算子定义配置文件**   

>[!NOTE]说明   
>**知识点（可选阅读）：msOpGen 输入配置文件**   
>自定义格式的 json 配置文件，可以简单类比理解为定义了一个 C 语言函数的声明，包括：函数名、入参及返回值的类型信息。
>比如 msopgen_demo.json 中就是定义了算子的名字、输入输出变量的名字、类型、数据排布格式。
>算子函数的声明代码统一由工具生成，即生成一个空函数（只有函数名、入参和返回值），函数体需要用户自己实现。

因是快速入门，将准备好的配置文件拷贝到此即视为开发完成（本教程聚焦工具链使用，实际开发需自行实现）：

```shell
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/msopgen_demo.json ./
```

**3. 基于配置生成代码框架**   
执行以下命令生成 Ascend C 算子工程，参数说明：-lan cpp 表明要生成 Ascend C 代码；-c 为芯片 SoC 型号（不同芯片处理上可能有区别）：

```shell
msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
```

**4. 查看生成的结果**   
>[!NOTE]说明   
>**知识点（可选阅读）：关键概念**       
> Host 侧：运行于 CPU 的代码，负责数据预处理、任务调度及算子调用。   
> Kernel 侧：运行于 NPU 的代码，负责执行实际的大规模并行计算逻辑。   
> Tiling：将大规模数据分块处理，以提高 Local Memory 利用率并优化内存访问效率。

生成的工程结构看起来庞大而复杂，但我们**仅需关注标记为【用户扩展点】的三个C++文件**，其余均为框架代码，无特殊需求无需查看修改：

```text
AddCustom
├── build.sh                 // 编译入口脚本
├── cmake                    // 编译工程脚本
├── CMakeLists.txt           // 算子工程的CMakeLists.txt
├── scripts                  // 自定义算子工程打包相关脚本所在目录
├── framework                // 算子插件实现文件目录，单算子模型文件的生成不依赖算子适配插件，无需关注
│   ├── CMakeLists.txt
│   └── tf_plugin
├── op_host                  // Host侧实现文件
│   ├── add_custom.cpp       // 【用户扩展点】算子原型注册、shape推导、信息库、tiling实现等内容文件
│   ├── add_custom_tiling.h  // 【用户扩展点】算子tiling定义文件
│   └── CMakeLists.txt
├── op_kernel                // Kernel侧实现文件
│   ├── add_custom.cpp       // 【用户扩展点】算子代码实现文件 
│   └── CMakeLists.txt
└── CMakePresets.json        // 编译配置项
```

#### 2.3.2 实现核心逻辑

>[!NOTE]说明   
>**知识点（可选阅读）：算子核心代码文件实现原理**    
>op_host/add_custom_tiling.h：定义 Tiling 分块策略的数据结构。   
>op_host/add_custom.cpp：实现 Host 侧的 Tiling 计算逻辑与算子原型注册。   
>op_kernel/add_custom.cpp：实现 Kernel 侧加法算子的具体计算逻辑（GM→UB 搬运→向量加法→UB→GM 写回）。   
>若需深入理解上述三个文件的功能与协作机制，除参考代码注释外，建议详细阅读<a href="https://www.hiascend.com/developer/blog/details/0239124507827469022" target="_blank">《昇腾Ascend C编程入门教程（纯干货）》</a>。

在上述三个【用户扩展点】文件中实现具体算法逻辑。因是快速入门，将准备好的 3 个 C++ 文件拷贝到此即视为开发完成（本教程聚焦工具链使用，实际开发需自行实现核心逻辑）：  

```shell
cd ~/ot_demo/workspace/src/AddCustom/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom_tiling.h ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom.cpp ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ./op_kernel/
```

#### 2.3.3 编译与部署算子

**1. 编译算子**  
执行构建脚本，成功后将在 build_out 目录下生成 .run 格式的算子部署包（sed 命令用于规避某些环境下的并发 pipe 问题，将打包改为串行）：

```shell
sed -i 's/--target $target -j$(nproc)/--target $target -j1/g' build.sh
bash ./build.sh
```

**2. 部署算子**   

>[!NOTE]说明   
>**知识点：什么是部署算子**  
> 部署算子是指将算子注册到 CANN 框架中，本质上是将算子的二进制文件拷贝至系统公共目录，使其他程序能够通过标准接口（如 CANN API 或 PyTorch 等）自动发现并调用该算子。*.run 的部署包格式可以简单理解为一种自解压的压缩包。

因各平台生成的算子部署包名称略有差异，执行以下脚本以自动定位并运行部署包（在固定环境中，实际等效于执行类似 ./build_out/custom_opp_ubuntu_aarch64.run 的命令）：

```shell
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

**3. 加入动态库路径**   
部署成功后，按终端提示追加算子依赖的动态库路径：

```shell
export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH
echo "export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
```

#### 2.3.4 验证算子功能

>[!CAUTION]注意   
>**关于 NPU 卡号的配置**   
>以下 run.sh 脚本将实际执行算子，默认使用 0 号 NPU 卡。若您必须使用其他卡，或 0 号卡运行算子异常而需要换用其他正常卡，请按如下方式修改卡号：     
>编辑 ~/ot_demo/workspace/src/caller/main.cpp 文件，在 main 函数首行将 deviceId 的值调整为目标 NPU 卡号。   
 
执行算子调用工程，验证算子功能（本例执行 1.0 + 2.0，预期结果为 3.0）：

```shell
\cp -rf ~/ot_demo/msot/example/quick_start/msopgen/caller ~/ot_demo/workspace/src/
cd ~/ot_demo/workspace/src/caller
bash ./run.sh
```

若输出如下内容，结果为 3.0，则表明算子已成功加载并计算正确：

```text
result is:
3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 
test pass
```

#### 2.3.5 备份 Kernel 侧 CMakeLists.txt

后续 3 个工具的执行都需要修改此 CMakeLists.txt，保留此备份，用于恢复环境：

```shell
\cp ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak
```

<br>

### 2.4 【检测】算子异常检测（msSanitizer）

算子开发完成后，可借助 msSanitizer 工具检测是否存在内存越界、竞争条件、未初始化变量或同步异常等严重运行时缺陷，从而高效定位潜在的隐蔽性错误。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.4.1 修改编译选项

为启用检测能力，需在 Kernel 侧的 CMakeLists.txt 首行插入 sanitizer 编译选项，注入检测桩代码：

```shell
cd ~/ot_demo/workspace/src/AddCustom
sed -i "1i\\add_ops_compile_options(ALL OPTIONS -sanitizer)" op_kernel/CMakeLists.txt
```

#### 2.4.2 构造内存越界错误

将准备好的含缺陷代码的源文件覆盖原始实现，人为引入越界访问：

```shell
\cp -f ~/ot_demo/msot/example/quick_start/mssanitizer/bug_code/add_custom.cpp op_kernel/add_custom.cpp
```

关键修改如下（2 * this->tileLength 试图读取 2 倍长度，超出 GM 内存中 xGm 的分配范围，触发 “非法读取”）：

```diff
- AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], this->tileLength);
+ AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], 2 * this->tileLength);
```

#### 2.4.3 重新编译部署

```shell
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

#### 2.4.4 执行内存检测

```shell
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck bash run.sh
```

工具输出如下错误报告，则表明已成功执行：  

1. illegal read of size 224：表示非法读取了 224 字节。   
2. op_kernel/add_custom.cpp:44:9：表明越界访问发生在 add_custom.cpp 第 44 行。   

```text
====== ERROR: illegal read of size 224
======    at 0x12c0c001af00 on GM in AddCustom_ab1b6750d7f510985325b603cb06dc8b_0
======    in block aiv(7) on device 0
======    code in pc current 0x2928 (serialNo:555)
======    #0 /usr/local/Ascend/ascend-toolkit/8.3.RC2/aarch64-linux/tikcpp/tikcfw/impl/dav_c220/kernel_operator_data_copy_impl.h:77:9
======    #1 /usr/local/Ascend/ascend-toolkit/8.3.RC2/aarch64-linux/tikcpp/tikcfw/impl/kernel_operator_data_copy_intf_impl.h:53:9
======    #2 /usr/local/Ascend/ascend-toolkit/8.3.RC2/aarch64-linux/tikcpp/tikcfw/impl/kernel_operator_data_copy_intf_impl.h:502:5
======    #3 /home/mgx/ot_demo/workspace/src/caller/AddCustom/op_kernel/add_custom.cpp:44:9
======    #4 /home/mgx/ot_demo/workspace/src/caller/AddCustom/op_kernel/add_custom.cpp:33:13
======    #5 /home/mgx/ot_demo/workspace/src/caller/AddCustom/op_kernel/add_custom.cpp:83:8
======    #6 /home/mgx/ot_demo/workspace/src/caller/AddCustom/build_out/op_kernel/AddCustom_ascend910b/kernel_0/kernel_meta_AddCustom_ab1b6750d7f510985325b603cb06dc8b/kernel_meta/AddCustom_ab1b6750d7f510985325b603cb06dc8b_2130445_kernel.cpp:37:5
```

#### 2.4.5 恢复手工修改

为后续工具使用做准备，回退手工修改：

```shell
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ~/ot_demo/workspace/src/AddCustom/op_kernel/
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

<br>

### 2.5 【调试】断点调试算子代码（msDebug）

若算子功能异常，可借助 msDebug 工具进行断点调试，高效定位问题。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.5.1 开启内核调试开关
>
>[!CAUTION]注意   
>**msDebug 需要 root 权限**       
> msDebug 需要内核调试开关 /proc/debug_switch 开启才能正常工作，但出于安全考虑默认关闭，且需要 root 权限才能打开。   
> 这在很多环境（如共享开发机、容器）中可能无法满足，此时请联系系统管理员开启，或在拥有特权的容器中体验此部分。

确认内核调试开关 debug_switch 是否打开：

```shell
cat /proc/debug_switch
```

若输出值不为 1，请使用 root 权限执行以下命令：

```shell
echo 1 > /proc/debug_switch
```

如果不能成功设置为 1，msDebug 功能不可用，只能跳过此节 msDebug 的体验。

#### 2.5.2 修改编译选项并重新部署

**1. 修改编译选项**   
在 Kernel 侧 CMakeLists.txt 首行插入一行配置，用于启用调试信息、禁用编译优化：

```shell
cd ~/ot_demo/workspace/src/AddCustom
sed -i "1i\\add_ops_compile_options(ALL OPTIONS -g -O0)" op_kernel/CMakeLists.txt
```

**2. 重新编译部署算子**

```shell
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

#### 2.5.3 设置调试环境变量

通过脚本设置 LAUNCH_KERNEL_PATH，指定算子obj加载路径并导入调试符号信息：

```shell
source ~/ot_demo/msot/example/quick_start/msdebug/set_kernel_obj_env.sh
```

#### 2.5.4 断点调试与变量查看

**1. 启动调试器**

```shell
cd ~/ot_demo/workspace/src/caller/build
msdebug execute_add_op
```

**2. 设置断点**   
待 (msdebug) 提示符出现后，设置断点于 add_custom.cpp 第 34 行：

```text
b add_custom.cpp:34
```

**3. 运行算子**   
输入 run 启动程序，等待命中断点：

```shell
run
```

显示如下信息，则成功命中断点：

```text
Process 163027 launched: '/root/ot_demo/workspace/src/caller/build/execute_add_op' (aarch64)
[Launch of Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 on Device 0]
Process 163027 stopped
[Switching to focus on Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0, CoreId 1, Type aiv]
* thread #1, name = 'execute_add_op', stop reason = breakpoint 1.1
    frame #0: 0x00000000000007e0 AddCustom_ab1b6750d7f510985325b603cb06dc8b.o`KernelAdd::Init(this=0x00000000001d78a8, x=0x12c0c0013000, y=0x12c0c001c000, z=0x12c0c0025000, totalLength=16384, tileNum=8) (.vector) at add_custom.cpp:34:9
   31           this->tileLength = this->blockLength / tileNum / BUFFER_NUM;
   32  
   33           // 设置全局内存缓冲区，为当前AI Core分配其负责的全局共享内存区域
-> 34           xGm.SetGlobalBuffer((__gm__ DTYPE_X *)x + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
   35           yGm.SetGlobalBuffer((__gm__ DTYPE_Y *)y + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
   36           zGm.SetGlobalBuffer((__gm__ DTYPE_Z *)z + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
```

**4. 查看变量的值**   
在断点处执行以下命令，显示当前作用域内的所有局部变量：

```text
var
```

**5. 退出调试器**

```text
q
```

#### 2.5.5 恢复手工修改

为后续工具使用做准备，回退手工修改：

```shell
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

<br>

### 2.6 【调优】分析算子性能（msOpProf）

若算子性能未达预期，可借助 msOpProf 工具采集运行时性能数据，进行深入分析与优化，确保算子在不同昇腾硬件平台上高效执行。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.6.1 修改编译选项并重新编译部署

**1. 修改编译选项**   
在 Kernel 侧 CMakeLists.txt 首行插入一行配置，开启调试信息：

```shell
cd ~/ot_demo/workspace/src/AddCustom
sed -i "1i\\add_ops_compile_options(ALL OPTIONS -g)" op_kernel/CMakeLists.txt
```

>[!NOTE]说明   
>**知识点（可选阅读）：为何 -O 优化等级在各工具间切来切去**   
>调试阶段为支持断点与变量查看，必须使用 -O0 关闭优化，以保留准确的符号映射；但 -O0 与 -O2 的性能差距可达数倍，因此性能分析必须基于 -O2（或默认优化级别）编译的代码，否则采集的数据将严重偏离真实场景，失去参考价值。

**2. 重新编译部署算子**   

```shell
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

#### 2.6.2 启动真机与仿真采集

>[!NOTE]说明   
>**知识点：上板和仿真采集信息的区别**   
> 上板：可精确捕获算子运行耗时、各 Pipe 使用情况、内存带宽、Cache 行为等真实硬件特性，而这些往往是仿真器难以高保真复现的关键指标。  
> 仿真：在指令流追踪、代码热点定位等方面提供更完整、稳定的分析能力，但对内存访问延迟、带宽瓶颈等硬件相关行为的模拟精度有限。  
> 因此，建议结合两种方式，互补优势，实现全面性能诊断。若某些场景下您没有真实硬件（NPU 卡），可以使用仿真模式进行初步的性能估算和热点分析。

**1. 上板性能采集**  

```shell
cd ~/ot_demo/workspace/src/caller/build
msprof op --output=./msprof_output_npu ./execute_add_op
```

**2. 仿真器性能采集**   

```shell
msprof op simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msprof_output_sim ./execute_add_op
```

#### 2.6.3 查看性能数据结果

工具在指定 --output 目录下生成 .csv 和 .bin 格式的结果文件，若输出未报错，则表明执行成功：

- csv 文件   
例如 MemoryUB.csv，打开可以看到如下信息：  
数据显示任务被均分为 8 个 block，全部调度至 Vector Core 执行。例如 Block 0 的带宽（1.02 GB/s）明显高于 Block 1（0.77 GB/s），如果差异过大，可能提示存在优化空间：

| block_id | sub_block_id | aiv_time(us) | aiv_total_cycles | aiv_ub_read_bw_vector(GB/s) | aiv_ub_write_bw_vector(GB/s) | 
|:--------:|:------------:|:------------:|:----------------:|:---------------------------:|:----------------------------:|
|    0     |   vector0    |  7.456666  |      13422      |          1.023164           |           0.511582           | 
|    1     |   vector0    |  9.914444  |      17846      |          0.769523           |           0.384762           | 
|    2     |   vector0    |  10.001111 |      18002      |          0.762855           |           0.381427           | 
|    3     |   vector0    |  9.684444  |      17432      |          0.787799           |           0.393899           | 
|    4     |   vector0    |  9.747222  |      17545      |          0.782725           |           0.391363           | 
|    5     |   vector0    |  9.062222  |      16312      |          0.84189            |           0.420945           | 
|    6     |   vector0    |  9.293889  |      16729      |          0.820904           |           0.410452           | 
|    7     |   vector0    |  8.658889  |      15586      |          0.881105           |           0.440553           | 

- bin 文件   
可使用 `MindStudio Insight` 工具打开，以图形化方式直观展示各类性能视图，例如：计算内存热力图、Cache 热力图以及算子代码热点图等。      

>[!NOTE]说明  
>若想体验可视化的图表查看，请参考<a href="https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/user_guide/mindstudio_insight_install_guide.md" target="_blank">《MindStudio Insight工具文档》</a>安装 Insight 工具。

#### 2.6.4 恢复手工修改

为后续工具使用做准备，回退手工修改：

```shell
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

<br>

### 2.7 【结业】恭喜您完成算子开发工具链入门体验

至此，您已完整走通"设计 → 开发 → 检测 → 调试 → 调优"的算子开发全流程，并实际体验了以下五个核心工具的基本用法：

| 工具          | 您已掌握的核心能力                         |
| ----------- | --------------------------------- |
| **msKPP**       | 编写 DSL 脚本进行算子性能建模，在无硬件条件下预估性能瓶颈   |
| **msOpGen**     | 基于配置文件自动生成算子工程框架，完成编译、部署与功能验证     |
| **msSanitizer** | 注入检测桩代码，定位内存越界等运行时缺陷的源码位置         |
| **msDebug**     | 启动断点调试，在 NPU 算子代码中设置断点并查看变量       |
| **msOpProf**    | 通过上板与仿真两种模式采集性能数据，分析各 Block 的执行效率 |

#### 后续进阶路径

##### **第一步：巩固基础 —— 独立开发一个新算子**  

参考本教程中的 AddCustom，尝试独立实现一个减法算子（SubCustom）或乘法算子（MulCustom），重点关注：Tiling 策略的设计差异、不同计算指令（如 `vsub`、`vmul`）的使用，以及端到端的编译部署流程。

##### **第二步：深入工具 —— 掌握各工具的高级功能**  

本教程仅覆盖了各工具的入门用法，每个工具都提供了更丰富的高级能力，建议按需访问对应仓的《使用指南》等深入学习：

| 工具 | 高级能力说明 |
|------|--------------|
| **msKPP** | 使用Cache命中率、随路转换等建模、多种 Tiling 方案的性能对比分析等。 |
| **msOpGen** | 复杂算子模板定制、多输入多输出算子的工程生成等。 |
| **msSanitizer** | 竞争条件检测、同步异常诊断、未初始化变量检查等更多检测模式。 |
| **msDebug** | 内存查看、核切换、解析Core dump文件等高级调试技巧。 |
| **msOpProf** | 结合 [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/user_guide/mindstudio_insight_install_guide.md) 进行可视化性能分析，包括计算内存热力图、Cache 热力图及代码热点图。 |

##### **第三步：落地真实业务 —— 从教学走向生产**  

深入研读[《Ascend C 编程指南（官方教程）》](https://www.hiascend.com/zh/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll)，系统掌握多级流水、数据排布、内存管理等核心概念，在此基础上尝试将工具链应用于实际业务算子的开发与调优，逐步构建从原型验证到生产级交付的完整能力。

### 2.8 【FAQ】常见错误解决

#### 2.8.1 执行 mskpp_demo.py 报错如下，怎么解决？

```text
root@localhost:~/ot_demo/workspace/mskpp# python3 mskpp_demo.py
Traceback (most recent call last):
  File "/root/ot_demo/workspace/mskpp/mskpp_demo.py", line 28, in <module>
    with Chip("Ascend" + chip_name) as chip:  # 格式为Ascendxxxyy，其中xxxyy为用户实际使用的具体芯片SoC型号，可通过npu-smi info查询
         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mskpp/core/chip.py", line 30, in __init__
    self.param_transfer()
  File "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mskpp/core/chip.py", line 110, in param_transfer
    raise Exception("Parameter chip_name in Chip is unsupported")
Exception: Parameter chip_name in Chip is unsupported
```

**问题原因：** `MY_STUDY_VAR_CHIP_SOC_TYPE` 环境变量丢失。   
**解决方法：** 参考[第 1.2 节](#12-环境准备)中《安装指南》的 1.3 节重新设置。

#### 2.8.2 编译调用算子程序时报错如下，怎么解决？

```text
-- Build files have been written to: /root/ot_demo/workspace/src/caller/build
[ 50%] Building CXX object CMakeFiles/execute_add_op.dir/main.cpp.o
/root/ot_demo/workspace/src/caller/main.cpp:16:10: fatal error: aclnn_add_custom.h: No such file or directory
   16 | #include "aclnn_add_custom.h"
      |          ^~~~~~~~~~~~~~~~~~~~
compilation terminated.
gmake[2]: *** [CMakeFiles/execute_add_op.dir/build.make:76: CMakeFiles/execute_add_op.dir/main.cpp.o] Error 1
gmake[1]: *** [CMakeFiles/Makefile2:83: CMakeFiles/execute_add_op.dir/all] Error 2
```

**问题原因：** 算子部署时没有将 op_api/include/aclnn_add_custom.h 部署到正确位置，导致找不到头文件。一种可能的原因是环境中存在环境变量 `ASCEND_CUSTOM_OPP_PATH`，且其值不正确或包含多个以冒号间隔的路径，但部署头文件时只会成功拷贝到第一个路径，后续目录均未部署。   
**解决方法：** 删除该环境变量（执行 `unset ASCEND_CUSTOM_OPP_PATH`），然后重新部署算子。   

#### 2.8.3 执行 execute_add_op 时异常，报错如下，怎么解决？

```text
execute_add_op: symbol lookup error: ./build/execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize
```

**问题原因：** 部署完算子后，没有按输出提示将 so 加入环境变量 LD_LIBRARY_PATH 中。   
**解决方法：** 按[第 2.3.3 节](#233-编译与部署算子)第 3 步，重新设置 LD_LIBRARY_PATH 环境变量。   

#### 2.8.4 执行 msDebug 设置断点时报错如下，怎么解决？

```text
(msdebug) b add_custom.cpp:23
Breakpoint 1: no locations (pending on future shared library load).
WARNING:  Unable to resolve breakpoint to any actual locations.
```

**问题原因：** 指定的断点行可能是空行或注释等无法设置断点的行。   
**解决方法：** 查看代码源文件，确认代码的真实行号。  

#### 2.8.5 执行 workspace/src/caller/run.sh 卡住不动？

**问题原因：** 因默认使用 0 号卡运行，可能 0 号卡繁忙或异常。   
**解决方法：** 执行 npu-smi info 查看是否有其他空闲卡，然后修改 caller/main.cpp 中 main 函数第 1 行，将 deviceId 的值修改为其他空闲卡号。
