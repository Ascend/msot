# 算子开发工具链快速入门

<br>

## 1. 概述

MindStudio 算子开发工具链包含多种工具。本文档以开发一个简单加法算子为例，带您贯穿算子开发全流程，直观体验工具链带来的高效与便捷。

**体验地图 (核心操作仅需 10 分钟，容器环境安装好后可全程 Copy/Paste 快速执行)**     
> **执行顺序建议**：步骤 1 为基础；完成 1 后可体验 2 或 3；步骤 4、5、6 均依赖步骤 3 生成的工程，但这三者之间相互独立，可按需选学。
 
 | 步骤 | 环节 | 核心工具 | 实测操作耗时 | 建议原理学习 |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **环境准备** | `CANN容器镜像` | 3分钟 | 5分钟 |
| **2** | **算子设计** | `msKPP` | 30 秒 | 5分钟 |
| **3** | **工程开发** | `msOpGen` | 1 分钟 | 20分钟 |
| **4** | **异常检测** | `msSanitizer` | 1 分钟 | 10分钟 |
| **5** | **原生调试** | `msDebug` | 1 分钟 | 10分钟 |
| **6** | **性能调优** | `msOpProf` | 1 分钟 | 10分钟 |

## 2. 操作步骤

### 2.1【环境】必备环境准备（强制前置 ⚠️）

🛑 **本节为强制前置步骤！跳过将导致后续操作大量出现失败。**  
本教程**仅支持**标准化 CANN 容器环境，不兼容裸机、虚拟机或其他非标准容器部署。

#### 2.1.1 安装 CANN 容器环境

✅ **请严格按以下指南完成环境安装：**  
👉 **[《昇腾 AI 算子开发工具链学习环境安装指南》](installation_guide.md)**

> ⏱️ **外网可达环境下预计耗时：约 3 分钟（具体时间受网络状况影响）**  
> 安装完成后，您将获得一个预装所有算子工具、示例代码和依赖库的标准化容器环境。

#### 2.1.2 执行环境自检脚本（必须通过！）

在如下正式体验前，请**全文复制下方整段脚本**，粘贴到终端执行，只有输出全部显示为 [PASS] 才能继续：

```bash
# 1. 容器环境检查
[ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ] && echo -e "\033[32m[PASS] CANN container environment OK \033[0m" || echo -e '\033[31m[FAIL] Non-standard container or not inside the container!\033[0m'
# 2. 芯片型号变量检查
[ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip Soc type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e "\033[31m[FAIL] Missing environment variable \$MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m"
# 3. 示例代码仓检查
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] Example code repository OK\033[0m" || echo -e "\033[31m[FAIL] Code repository missing\033[0m"
```

🚀 **后续体验环节全程支持 Copy/Paste 快速执行，请按照每节中的步骤顺序操作，勿跳过或打乱操作步骤。**

### 2.2【设计】算子建模设计（msKPP）

首先，进行算子算法设计。借助 msKPP 工具，可在秒级时间内获得算子性能建模结果，在无硬件条件下预估性能，快速验证实现方案的可行性。先跟着操作体验效果，原理部分可稍后阅读：

> [!NOTE]说明   
> 
> **知识点：msKPP 工具原理**   
> msKPP 并非传统可执行程序，而是一套专用于昇腾的 Python 类库。用户需通过 import 相关模块、编写并执行 Python 脚本，生成性能分析结果文件以完成建模。内部原理是预先采集真实环境中各类指令操作的性能数据，基于用户定义的算子执行流程，对各种性能开销进行建模与估算。

#### 2.2.1 环境检查

本工具**仅支持昇腾 910B** 系列芯片。请执行以下命令：

```bash
chip=$(npu-smi info -m 2>/dev/null | grep -oP 'Ascend\s*\S+' | head -1); case "$chip" in 'Ascend 910B'* ) echo -e "\n\e[32m[PASS] Chip SoC type [$chip] check passed. Please continue with the experience.\e[0m";; * ) echo -e "\n\033[31m[FAIL] Get chip: ${chip:-None}. The current environment does not support this tool. Please skip this experience.\033[0m" >&2;; esac
```

若输出为 `[PASS]`，请继续进行体验；若输出为 `[FAIL]`，请切换至搭载昇腾 910B 芯片的环境后再进行体验；否则，请跳过本节内容。

#### 2.2.2 编写 Python 建模脚本

1. 创建子工作区目录

    ```bash
    mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
    ```

2. 开发 Python 脚本

    > [!NOTE]说明  
    > 
    > **知识点（可选阅读）：msKPP 的 DSL 语言方案（Domain-Specific Language，领域特定语言）**   
    > 这套类库及接口是专为昇腾性能建模而设计的“方言”，需经过专门学习方可掌握，无法仅凭通用 Python 语法直接编写，但用法较简单，稍加学习即可应用。
    > 常规开发流程：需先导入 Tensor、Chip 以及算子实现所必需的指令（例如 vadd），通过 with 语句进入算子实现代码的上下文，再创建 Tensor 以执行具体操作，样例脚本中已做了详细的注释，其他指令接口说明请参考《[msKPP 工具接口说明](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/api_reference/mskpp_api_reference.md)》。

    因是快速入门，将准备好的 msKPP 的 DSL 脚本复制到此即视为开发完成（本教程聚焦工具链使用，实际开发需自行实现）：

    ```bash
    \cp -f ~/ot_demo/msot/example/quick_start/mskpp/mskpp_demo.py ./
    ```

#### 2.2.3 执行性能建模

执行 Python 脚本开始性能建模，如果成功，将自动在当前目录下生成 "MSKPP{timestamp}" 结果目录：

```bash
python3 mskpp_demo.py
```

如果脚本报错，提示 Chip is unsupported，请确认环境变量 `MY_STUDY_VAR_CHIP_SOC_TYPE` 是否正确设置，如变量为空，请参考《[算子开发工具链学习环境安装指南](./installation_guide.md)》的第 3 节重新设置；若变量非空，请核实当前芯片型号是否为 910B 系列——本工具仅支持 910B 系列芯片，请切换至 910B 系列芯片环境后再进行体验。

#### 2.2.4 查看建模结果

以下为部分生成结果文件的示例：

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

由上述内容可见，MOV-UB_TO_GM（从 UB 搬移到 GM）的耗时（Duration）最长，指令周期数（Cycle）也最多，是性能优化中需重点关注的关键路径。在实际开发中，如果发现此类内存搬运耗时占比过高，应优先考虑优化数据复用（Tiling）或使用更高效的搬运指令。

### 2.3【开发】构建算子工程（msOpGen）

算法设计完成后，即可进入算子代码编写阶段。算子工程较为复杂且包含大量框架代码，msOpGen 工具可自动生成完整的算子工程框架，使开发者聚焦于核心算法实现，避免在项目搭建、编译配置等重复性工作上耗费时间。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.3.1 生成工程框架

1. 创建子工作区目录

    创建名为 `src` 的子目录，作为算子源码根目录，后续所有源码操作均基于此路径开展：

    ```bash
    mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src/
    ```

2. 开发算子定义配置文件

    > [!NOTE]说明   
    > 
    > **知识点（可选阅读）：msOpGen 输入配置文件**   
    > 自定义格式的 json 配置文件，可以简单类比理解为定义了一个 C 语言函数的声明，包括：函数名、入参及返回值的类型信息。
    > 比如 msopgen_demo.json 中就是定义了算子的名字、输入输出变量的名字、类型、数据排布格式。
    > 算子函数的声明代码统一由工具生成，即生成一个空函数（只有函数名、入参和返回值），函数体需要用户自己实现。

    因是快速入门，将准备好的配置文件拷贝到此即视为开发完成（本教程聚焦工具链使用，实际开发需自行实现）：

    ```bash
    \cp -f ~/ot_demo/msot/example/quick_start/msopgen/msopgen_demo.json ./
    ```

3. 基于配置生成代码框架

    执行以下命令生成 Ascend C 算子工程，参数说明：-lan cpp 表明要生成 Ascend C 代码；-c 为芯片 SoC 型号（不同芯片处理上可能有区别）：

    ```bash
    msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
    ```

    >[!CAUTION]注意          
    > 上述命令生成的代码框架中，具体算子的实现为空，无法正常执行加法运算，需按照 [2.3.2节](#232-实现核心逻辑) 内容进行修改后方可正常运行。 

    如需了解上述命令各参数的详细含义，请参阅 [msOpGen 代码仓库](https://gitcode.com/Ascend/msopgen) 的 《使用指南》。

4. 查看生成的结果

    > [!NOTE]说明   
    > 
    > **知识点（可选阅读）：关键概念**       
    > Host 侧：运行于 CPU 的代码，负责数据预处理、任务调度及算子调用。   
    > Kernel 侧：运行于 NPU 的代码，负责执行实际的大规模并行计算逻辑。   
    > Tiling：将大规模数据分块处理，以提高 Local Memory 利用率并优化内存访问效率。

    以下为部分生成结果文件的示例，生成的工程结构看起来庞大而复杂，但我们**仅需关注标记为【用户扩展点】的三个C++文件**，其余均为框架代码，无特殊需求无需查看修改：

    ```text
    AddCustom
    ├── build.sh                 // 编译入口脚本
    ├── CMakeLists.txt           // 算子工程的CMakeLists.txt
    ├── framework                // 算子插件实现文件目录，单算子模型文件的生成不依赖算子适配插件，无需关注
    │   ├── CMakeLists.txt
    │   └── tf_plugin
    ├── op_host                  // Host侧实现文件
    │   ├── add_custom.cpp       // 【用户扩展点】算子原型注册、shape推导、信息库、tiling实现等内容文件
    │   └── CMakeLists.txt
    ├── op_kernel                // Kernel侧实现文件
    │   ├── add_custom.cpp       // 【用户扩展点】算子代码实现文件 
    │   ├── add_custom_tiling.h  // 【用户扩展点】算子tiling定义文件   
    │   └── CMakeLists.txt
    └── CMakePresets.json        // 编译配置项
    ```

#### 2.3.2 实现核心逻辑

> [!NOTE]说明   
> 
> **知识点（可选阅读）：算子核心代码文件实现原理**  
> op_host/add_custom.cpp：实现 Host 侧的 Tiling 计算逻辑与算子原型注册。  
> op_kernel/add_custom_tiling.h：定义 Tiling 分块策略的数据结构。  
> op_kernel/add_custom.cpp：实现 Kernel 侧加法算子的具体计算逻辑（GM→UB 搬运→向量加法→UB→GM 写回）。   
> 若需深入理解上述三个文件的功能与协作机制，除参考代码注释外，建议详细阅读<a href="https://www.hiascend.com/developer/blog/details/0239124507827469022" target="_blank">《昇腾Ascend C编程入门教程（纯干货）》</a>。    
> 如下 `keep_soc_info.py` 原理说明：此脚本会自动获取当前环境的SoC信息，并自动刷新到cpp文件中。

在上述三个【用户扩展点】文件中实现具体算法逻辑。因是快速入门，将准备好的 3 个 C++ 文件拷贝到此即视为开发完成（本教程聚焦工具链使用，实际开发需自行实现核心逻辑）：  

```bash
cd ~/ot_demo/workspace/src/AddCustom/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py get ./op_host/add_custom.cpp # 获取当前环境SoC信息
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom.cpp ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom_tiling.h ./op_kernel/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ./op_kernel/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py set ./op_host/add_custom.cpp # 刷新代码中SoC信息为当前环境SoC信息
```

#### 2.3.3 编译与部署算子

1. 编译算子

    执行构建脚本，成功后将在 build_out 目录下生成 .run 格式的算子部署包：

    ```bash
    bash ./build.sh
    ```

2. 部署算子  

    >[!NOTE]说明   
    > 
    > **知识点：什么是部署算子**  
    > 部署算子是指将算子注册到 CANN 框架中，本质上是将算子的二进制文件拷贝至系统公共目录，使其他程序能够通过标准接口（如 CANN API 或 PyTorch 等）自动发现并调用该算子。*.run 的部署包格式可以简单理解为一种自解压的压缩包。

    因各平台生成的算子部署包名称略有差异，执行以下脚本以自动定位并运行部署包（在固定环境中，实际等效于执行类似 ./build_out/custom_opp_ubuntu_aarch64.run 的命令）：

    ```bash
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

3. 加入动态库路径
      
    部署成功后，按终端提示追加算子依赖的动态库路径：

    ```bash
    export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH
    echo "export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
    ```

#### 2.3.4 验证算子功能

> [!CAUTION]注意   
> **关于 NPU 设备选择的说明**   
> 执行以下 `run.sh` 脚本将实际运行算子，会随机选择一张空闲卡执行任务。
> 若因随机选定的卡存在故障等原因需指定 NPU 卡，请根据 `npu-smi info` 命令返回的 NPU 信息，使用其顺序号（取值范围为 [0, NPU 数量 - 1]）按如下方式调用：`bash ./run.sh 2`

执行算子调用工程，验证算子功能（本例执行 1.0 + 2.0，预期结果为 3.0）：

```bash
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

若未能看到上述输出，请参照下表排查：

| 现象 | 可能原因 | 处理方式 |
|------|----------|----------|
| 超过 30 秒无返回 | NPU 卡繁忙 | 按 Ctrl+C 终止，切换至其他空闲卡重试（指定方法见上文”关于 NPU 设备选择的说明”） |
| 出现如下 ACL 报错 | NPU 卡异常（硬件故障、驱动问题等）；<br>`/dev/hisi_hdc` 设备异常，比如未挂载、无权限等；<br>内存等系统资源不足； | 解决 NPU 卡故障或更换为正常卡后重试；错误码含义参见[《ACL 错误码表》](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850/API/appdevgapi/aclcppdevg_03_1345.html) |

```text
aclrtSetDevice failed. ERROR: xxxxxx
Init acl failed. ERROR: 1
```

#### 2.3.5 备份 Kernel 侧 CMakeLists.txt

后续 3 个工具的执行都需要修改此 CMakeLists.txt，保留此备份，用于恢复环境：

```bash
\cp ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak
```

### 2.4【检测】算子异常检测（msSanitizer）

算子开发完成后，可借助 msSanitizer 工具检测是否存在内存越界、竞争条件、未初始化变量或同步异常等严重运行时缺陷，从而高效定位潜在的隐蔽性错误。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.4.1 修改编译选项

为启用检测能力，需在 Kernel 侧的 CMakeLists.txt 首行插入 sanitizer 编译选项，注入检测桩代码：

```bash
cd ~/ot_demo/workspace/src/AddCustom
sed -i '1i npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)' op_kernel/CMakeLists.txt
```

#### 2.4.2 构造内存越界错误

将准备好的含缺陷代码的源文件覆盖原始实现，**人为引入越界访问**：

```bash
\cp -f ~/ot_demo/msot/example/quick_start/mssanitizer/bug_code/add_custom.cpp op_kernel/add_custom.cpp
```

>[!NOTE]说明  
>关键修改如下，将 `AscendC::DataCopy` 函数调用中将读取长度修改为 2 倍（`2 * this->tileLength`），导致访问超出 GM 内存中 `xGm` 的分配范围，从而触发“非法读取”错误。

#### 2.4.3 重新编译部署

```bash
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

#### 2.4.4 执行内存检测

```bash
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck -- bash run.sh
```

工具输出如下错误报告，则表明已成功执行，识别到构造的越界访问（如下示例显示各版本可能会稍有不同，不影响学习工具使用）：  

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
======    #3 /root/ot_demo/workspace/src/caller/AddCustom/op_kernel/add_custom.cpp:44:9
======    #4 /root/ot_demo/workspace/src/caller/AddCustom/op_kernel/add_custom.cpp:33:13
======    #5 /root/ot_demo/workspace/src/caller/AddCustom/op_kernel/add_custom.cpp:83:8
======    #6 /root/ot_demo/workspace/src/caller/AddCustom/build_out/op_kernel/AddCustom_ascend910b/kernel_0/kernel_meta_AddCustom_ab1b6750d7f510985325b603cb06dc8b/kernel_meta/AddCustom_ab1b6750d7f510985325b603cb06dc8b_2130445_kernel.cpp:37:5
```

> [!NOTE]说明  
> 算子执行后仍能成功输出正确结果，这正体现了该工具的价值：内存问题通常具有偶发性，在多数情况下即使存在内存异常，程序仍可正常运行；仅当问题累积至临界点时才会突发崩溃，难以通过表象直接定位。

#### 2.4.5 恢复手工修改

为后续工具使用做准备，回退手工修改：

```bash
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ~/ot_demo/workspace/src/AddCustom/op_kernel/
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.5【调试】断点调试算子代码（msDebug）

若算子功能异常，可借助 msDebug 工具进行断点调试，高效定位问题。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.5.1 开启内核调试开关

>[!CAUTION]注意    
> **msDebug 需以 root 权限启用内核调试开关 /proc/debug_switch**  
> 
> 该开关默认关闭，仅 root 用户可修改。msDebug 必须在该开关开启后才能正常工作。  
> 
> **容器中操作通常无效：**  
> 即使在容器内以 root 身份成功写入 `/proc/debug_switch`，由于宿主机普遍对 `/proc` 使用写时复制（CoW）、影子文件或 overlay 挂载等机制进行虚拟化，该设置**仅作用于容器视图**，并未真正生效于内核。因此，即便 `cat /proc/debug_switch` 显示为 `1`，msDebug 仍可能无法使用，并在调试时返回错误（如 `'A' packet returned an error: 8`）。  
> 
> **推荐做法：**  
> 若您处于共享开发机、普通容器或无宿主机访问权限的环境中，请联系系统管理员协助开启，或切换至具备 root 权限的宿主机环境体验本功能。

确认内核调试开关 debug_switch 是否打开：

```bash
cat /proc/debug_switch
```

若输出值不为 1，请使用 root 权限在宿主机执行以下命令： 

```bash
echo 1 > /proc/debug_switch
```

如果不能成功设置为 1，msDebug 功能不可用，只能跳过此节 msDebug 的体验。

#### 2.5.2 修改编译选项并重新部署

1. 修改编译选项

    在 Kernel 侧 CMakeLists.txt 首行插入配置，用于启用调试信息、禁用编译优化：

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    sed -i '1i npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)' op_kernel/CMakeLists.txt
    ```

2. 重新编译部署算子

    ```bash
    bash ./build.sh
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

#### 2.5.3 设置调试环境变量

通过脚本设置 LAUNCH_KERNEL_PATH，指定算子obj加载路径并导入调试符号信息：

```bash
source ~/ot_demo/msot/example/quick_start/msdebug/set_kernel_obj_env.sh
```

#### 2.5.4 断点调试与变量查看

1. 启动调试器

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msdebug execute_add_op
    ```

2. 设置断点
      
    待 (msdebug) 提示符出现后，设置断点于 add_custom.cpp 第 34 行：

    ```text
    b add_custom.cpp:34
    ```

    >[!CAUTION]注意  
    >若此前未在宿主机正确启用 /proc/debug_switch，执行上述断点设置将触发警告，而在后续步骤运行 `run` 命令时将触发调试器错误（例如 'A' packet returned an error: 8），表明 msDebug 无法正常工作。

3. 运行算子
      
    输入 run 启动程序，等待命中断点：

    ```text
    run
    ```

    显示如下信息，则成功命中断点（如下示例显示各版本可能会稍有不同，不影响学习工具使用）：

    ```text
    Process 2799 launched: '/root/ot_demo/workspace/src/caller/build/execute_add_op' (aarch64)
    Running on NPU [0]. If this is the first run on this card, scheduling may take a few seconds; please wait...
    [Launch of Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 on Device 0]
    1 location added to breakpoint 1
    Process 2799 stopped
    [Switching to focus on Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0, CoreId 35, Type aiv]
    * thread #1, name = 'execute_add_op', stop reason = breakpoint 1.2
        frame #0: 0x000012c0412008b4 device_debugdata_0`KernelAdd::Init(this=0x00000000002e7860, x=0x12c0c0015000, y=0x12c0c001e000, z=0x12c0c0027000, totalLength=16384, tileNum=8) (.vector) at add_custom.cpp:34:9
       31           this->tileLength = this->blockLength / this->tileNum / BUFFER_NUM;
       32  
       33           // 设置全局内存缓冲区，为当前AI Core分配其负责的全局共享内存区域
    -> 34           xGm.SetGlobalBuffer((__gm__ DTYPE_X *)x + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
       35           yGm.SetGlobalBuffer((__gm__ DTYPE_Y *)y + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
       36           zGm.SetGlobalBuffer((__gm__ DTYPE_Z *)z + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
    ```

4. 查看变量的值
      
    在断点处执行以下命令，显示当前作用域内的所有局部变量：

    ```text
    var
    ```

5. 退出调试器

    ```text
    q
    ```

#### 2.5.5 恢复手工修改

为后续工具使用做准备，回退手工修改：

```bash
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.6【调优】分析算子性能（msOpProf）

若算子性能未达预期，可借助 msOpProf 工具采集运行时性能数据，进行深入分析与优化，确保算子在不同昇腾硬件平台上高效执行。先跟着操作体验效果，原理部分可稍后阅读：

#### 2.6.1 修改编译选项并重新编译部署

1. 修改编译选项
    
    在 Kernel 侧 CMakeLists.txt 首行插入一行配置，开启调试信息：

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    sed -i '1i npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)' op_kernel/CMakeLists.txt
    ```

    > [!NOTE]说明   
    > 
    > **知识点（可选阅读）：为何 -O 优化等级在各工具间切来切去**   
    > 调试阶段为支持断点与变量查看，必须使用 -O0 关闭优化，以保留准确的符号映射；但 -O0 与 -O2 的性能差距可达数倍，因此性能分析必须基于 -O2（或默认优化级别）编译的代码，否则采集的数据将严重偏离真实场景，失去参考价值。

2. 重新编译部署算子

    ```bash
    bash ./build.sh
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

#### 2.6.2 启动真机与仿真采集

> [!NOTE]说明   
> **知识点：上板和仿真采集信息的区别**   
> 上板：可精确捕获算子运行耗时、各 Pipe 使用情况、内存带宽、Cache 行为等真实硬件特性，而这些往往是仿真器难以高保真复现的关键指标。  
> 仿真：在指令流追踪、代码热点定位等方面提供更完整、稳定的分析能力，但对内存访问延迟、带宽瓶颈等硬件相关行为的模拟精度有限。  
> 因此，建议结合两种方式，互补优势，实现全面性能诊断。若某些场景下您没有真实硬件（NPU 卡），可以使用仿真模式进行初步的性能估算和热点分析。

1. 上板性能采集 

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msopprof --output=./msopprof_output_npu ./execute_add_op
    ```

2. 仿真器性能采集

    ```bash
    msopprof simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msopprof_output_sim ./execute_add_op
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

  > [!NOTE]说明  
  > 
  > 若想体验可视化的图表查看，请参考<a href="https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/install_guide/mindstudio_insight_install_guide.md" target="_blank">《MindStudio Insight工具文档》</a>安装 Insight 工具。

#### 2.6.4 恢复手工修改

为后续工具使用做准备，回退手工修改：

```bash
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.7【结业】后续进阶路径

恭喜您完成算子开发工具链入门体验。

至此，您已完整走通“设计 → 开发 → 检测 → 调试 → 调优”的算子开发全流程，并实际体验了以下五个核心工具的基本用法：

| 工具          | 您已掌握的核心能力                         |
| ----------- | --------------------------------- |
| **msKPP**       | 编写 DSL 脚本进行算子性能建模，在无硬件条件下预估性能瓶颈   |
| **msOpGen**     | 基于配置文件自动生成算子工程框架，完成编译、部署与功能验证     |
| **msSanitizer** | 注入检测桩代码，定位内存越界等运行时缺陷的源码位置         |
| **msDebug**     | 启动断点调试，在 NPU 算子代码中设置断点并查看变量       |
| **msOpProf**    | 通过上板与仿真两种模式采集性能数据，分析各 Block 的执行效率 |

如果您想继续进阶体验，可参考以下步骤：

**第一步：巩固基础 —— 独立开发一个新算子**  

参考本教程中的 AddCustom，尝试独立实现一个减法算子（SubCustom）或乘法算子（MulCustom），重点关注：Tiling 策略的设计差异、不同计算指令（如 `vsub`、`vmul`）的使用，以及端到端的编译部署流程。

**第二步：深入工具 —— 掌握各工具的高级功能**  

本教程仅覆盖了各工具的入门用法，每个工具都提供了更丰富的高级能力，建议按需访问对应仓的《使用指南》等深入学习：

| 工具 | 高级能力说明 |
|------|--------------|
| [msKPP](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/user_guide/mskpp_user_guide.md) | 使用Cache命中率、随路转换等建模、多种 Tiling 方案的性能对比分析等。 |
| [msOpGen](https://gitcode.com/Ascend/msopgen/blob/master/docs/zh/user_guide/msopgen_user_guide.md) | 复杂算子模板定制、多输入多输出算子的工程生成等。 |
| [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/master/docs/zh/user_guide/mssanitizer_user_guide.md) | 竞争条件检测、同步异常诊断、未初始化变量检查等更多检测模式。 |
| [msDebug](https://gitcode.com/Ascend/msdebug/blob/master/docs/zh/user_guide/msdebug_user_guide.md) | 内存查看、核切换、解析Core dump文件等高级调试技巧。 |
| [msOpProf](https://gitcode.com/Ascend/msopprof/blob/master/docs/zh/user_guide/msopprof_user_guide.md) | 结合 [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/install_guide/mindstudio_insight_install_guide.md) 进行可视化性能分析，包括计算内存热力图、Cache 热力图及代码热点图。 |

**第三步：落地真实业务 —— 从教学走向生产**  

深入研读[《Ascend C 编程指南（官方教程）》](https://www.hiascend.com/zh/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll)，系统掌握多级流水、数据排布、内存管理等核心概念，在此基础上尝试将工具链应用于实际业务算子的开发与调优，逐步构建从原型验证到生产级交付的完整能力。

## 3. FAQ

### 3.1 执行 mskpp_demo.py 报错：Exception: Parameter chip_name in Chip is unsupported

**问题现象**

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

**问题原因** 

`MY_STUDY_VAR_CHIP_SOC_TYPE` 环境变量丢失。

**解决方法** 

参考《[算子开发工具链学习环境安装指南](./installation_guide.md)》的第 3 节重新设置。

### 3.2 编译调用算子程序时报错：fatal error: aclnn_add_custom.h: No such file or directory

**问题现象**

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

**问题原因** 

算子部署时没有将 op_api/include/aclnn_add_custom.h 部署到正确位置，导致找不到头文件。一种可能的原因是环境中存在环境变量 `ASCEND_CUSTOM_OPP_PATH`，且其值不正确或包含多个以冒号间隔的路径，但部署头文件时只会成功拷贝到第一个路径，后续目录均未部署。

**解决方法** 

删除该环境变量（执行 `unset ASCEND_CUSTOM_OPP_PATH`），然后重新部署算子。

### 3.3 执行 execute_add_op 时异常报错：undefined symbol: aclnnAddCustomGetWorkspaceSize

**问题现象**

```text
execute_add_op: symbol lookup error: ./build/execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize
```

**问题原因** 

部署完算子后，没有按输出提示将 so 加入环境变量 LD_LIBRARY_PATH 中。

**解决方法** 

按[2.3.3 编译与部署算子](#233-编译与部署算子)第 3 步，重新设置 LD_LIBRARY_PATH 环境变量。

### 3.4 执行 msDebug 设置断点时报错：WARNING:  Unable to resolve breakpoint to any actual locations

**问题现象**

```text
(msdebug) b add_custom.cpp:23
Breakpoint 1: no locations (pending on future shared library load).
WARNING:  Unable to resolve breakpoint to any actual locations.
```

**问题原因** 

指定的断点行可能是空行或注释等无法设置断点的行，或者 `/proc/debug_switch` 没有成功设置，原因参考下节说明。

**解决方法** 

查看代码源文件，确认代码的真实行号；按 [2.5.1 开启内核调试开关](#251-开启内核调试开关) 以 root 权限在宿主机上（注意不是容器内）设置 `/proc/debug_switch` = 1。

### 3.5 执行 msDebug 的 run 时报错：error: 'A' packet returned an error: 8

**问题现象**

```text
error: 'A' packet returned an error: 8
```

**问题原因** 

没有成功设置`/proc/debug_switch = 1`。确认宿主机上是否被修改回0了，或者若您在云服务商提供的容器环境中操作的，这种场景即使在容器内成功将 `/proc/debug_switch` 设置并查询为 1，
该状态也可能是虚假的。因出于安全考虑，底层宿主机通常会通过写时复制（CoW）、影子文件或覆盖挂载（overlay mount）等机制对 /proc 目录进行隔离，导致设置未实际生效。

**解决方法** 

以 root 权限登录到宿主机上（注意不是容器内），按 [2.5.1 开启内核调试开关](#251-开启内核调试开关) 设置 `/proc/debug_switch` = 1，如果不能设置成功只能跳过此工具体验。

### 3.6 进入容器后发现 Python 版本异常或缺少大量依赖库

**问题现象**  
容器内 Python 版本异常，或存在大量依赖库缺失。

**问题原因**  
可能因使用公共账户，比如 `root` 账户进行操作所致。`root` 为多人共享账户，其配置文件（如 `~/.bashrc`）可能已被他人修改（例如配置了 Conda 环境）。容器启动时若挂载或继承了宿主机的 `~/.bashrc`，将导致 Python 环境被意外覆盖或干扰。

**解决方法**  
建议使用个人普通账户登录并进行体验，避免使用公共账户，以防止受共享配置影响而导致环境异常。
