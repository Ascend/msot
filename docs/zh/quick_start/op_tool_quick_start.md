# 算子开发工具链快速入门

<br>

## 1. 概述

MindStudio 算子开发工具链包含多种工具。本文档以开发一个简单加法算子为例，带您贯穿算子开发全流程，直观体验工具链带来的高效与便捷。

**体验地图（核心操作仅需 10 分钟，可全程 Copy/Paste 快速执行）**
> **执行顺序建议**：步骤 1 为基础；完成 1 后可体验 2 或 3；步骤 4、5、6 均依赖步骤 3 生成的工程，但这三者之间相互独立，可按需选学。

| 步骤 | 环节 | 核心工具 | 实测操作耗时 | 建议原理学习 |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **环境准备** | `CANN 容器镜像` | 3 分钟 | 5 分钟 |
| **2** | **算子设计** | `msKPP` | 30 秒 | 5 分钟 |
| **3** | **工程开发** | `msOpGen` | 1 分钟 | 20 分钟 |
| **4** | **异常检测** | `msSanitizer` | 1 分钟 | 10 分钟 |
| **5** | **原生调试** | `msDebug` | 1 分钟 | 10 分钟 |
| **6** | **性能调优** | `msOpProf` | 1 分钟 | 10 分钟 |

## 2. 操作步骤

### 2.1 必要环境准备

#### 2.1.1 安装 CANN 容器环境

本教程**仅支持**标准化 CANN 容器环境，不支持裸机、虚拟机或其他非标准容器部署。
**请按以下指南完成环境安装**，否则可能导致后续操作执行失败。
👉 **[《昇腾 AI 算子开发工具链学习环境安装指南》](installation_guide.md)**

> **具备公网访问能力的环境预计耗时：约 3 分钟（具体时间受网络状况影响）**
> 安装完成后，您将获得一个预装所有算子工具、示例代码和依赖库的标准化容器环境。

#### 2.1.2 环境自检

请在已加载 CANN 环境的容器内，使用 Bash 执行如下命令设置变量并检查环境：

```bash
source ~/ot_demo/msot/example/quick_start/scripts/set_chip_soc_env.sh &&
bash ~/ot_demo/msot/example/quick_start/scripts/check_env.sh --task core
```

回显 `Environment check successful, summary 0 failure(s).` 表示检查通过。

🚀 **后续体验环节都在容器内执行，由于入门体验过程中产物输出需要依赖复用，请按文档章节顺序依次执行。**

### 2.2【设计】算子建模设计（msKPP）

首先进行算子算法设计，借助 msKPP 工具，可在快速获得算子性能建模结果，在不依赖硬件条件下预估性能，快速验证实现方案的可行性。工具使用步骤如下：

> [!NOTE]说明   
> 
> **知识点：msKPP 工具原理**   
> msKPP 包含一套专用于昇腾的 Python 类库，用户需通过 `import` 相关模块、编写并运行 Python 脚本，生成性能分析结果文件与建模结果。

#### 2.2.1 环境检查

msKPP工具**仅支持昇腾 910B** 系列芯片，请执行以下命令校验芯片类型：

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/check_env.sh --task mskpp
```

输出 `Environment check successful`表示校验成功，可继续执行后续步骤；否则请切换至搭载昇腾 910B 芯片的环境后再进行体验，或跳过本节内容。

#### 2.2.2 开发建模脚本

1. 准备子工作区和建模样例

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/prepare_sample.sh --sample mskpp --dest ~/ot_demo/workspace/mskpp
cd ~/ot_demo/workspace/mskpp
```

输出 `Prepare sample successful` 表示执行成功。由于本文为快速入门，聚焦工具使用方法，因此准备了样例脚本，脚本路径见日志回显内容，实际开发时请根据需求内容自行实现或编辑。

> [!NOTE]说明  
> 
> **知识点（可选阅读）：msKPP 的 DSL 语言方案（Domain-Specific Language，领域特定语言）**   
> 这套类库及接口是专为昇腾性能建模而设计的“方言”，无法仅凭通用 Python 语法直接编写，但用法较简单，稍加学习即可应用。
> 常规开发流程：先导入 Tensor、Chip 以及算子实现所必需的指令（例如 vadd），通过 `with` 语句进入算子实现代码的上下文，再创建 Tensor 以执行具体操作，详细内容可参考样例脚本中相关注释，其他指令接口说明请参考《[msKPP 工具接口说明](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/api_reference/mskpp_api_reference.md)》。

#### 2.2.3 执行性能建模

执行如下命令 Python 脚本开始性能建模：

```bash
python3 mskpp_demo.py
```

输出 `MSKPP modeling completed successfully` 表示执行成功。将自动在当前目录下生成 `MSKPP{timestamp}` 结果目录，实际路径见日志回显。

#### 2.2.4 查看建模结果

以下为部分生成结果文件的示例：

```text
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

以 Instruction_statistic.csv 为例，其内容如下：

| Instruction  | Duration(μs) | Cycle | Size(Byte) | Ops  |
|:--------------:|:--------------:|:-------:|:---------:|:------:|
| MOV-GM_TO_UB |    0.3081    |  570  |  6144   |  -   |
|     VADD     |    0.0135    |  25   |    -    | 1536 |
| MOV-UB_TO_GM |    0.4254    |  787  |  3072   |  -   |

由上述内容可见，MOV-UB_TO_GM（从 UB 搬移到 GM）的耗时（Duration）最长，指令周期数（Cycle）也最多，是性能优化中需重点关注的关键路径。在实际开发中，如果发现此类内存搬运耗时占比过高，应优先考虑优化数据复用（Tiling）或使用更高效的搬运指令。

### 2.3【开发】构建算子工程（msOpGen）

算法设计完成后，即可进入算子代码编写阶段。算子工程通常包含大量框架代码，msOpGen 工具可自动生成完整的算子工程框架，使开发者聚焦于核心算法实现，避免在项目搭建、编译配置等重复性工作上耗费时间。工具使用步骤如下：

#### 2.3.1 生成工程框架

1. 准备子工作区和msOpGen输入配置文件

    执行如下脚本，创建 `src` 的子目录并准备算子定义配置文件：

    ```bash
   bash ~/ot_demo/msot/example/quick_start/scripts/prepare_sample.sh --sample opgen --dest ~/ot_demo/workspace/src
   cd ~/ot_demo/workspace/src/
   ```

   输出 `Prepare sample successful` 表示执行成功。由于本文为快速入门，聚焦工具使用方法，因此准备了算子定义样例 JSON 文件，文件路径见脚本日志回显内容，实际开发时请根据需求内容自行实现或编辑。

   > [!NOTE]说明   
   > 
   > **知识点（可选阅读）：msOpGen 输入配置文件**   
   > 算子定义的JSON配置文件，用于结构化定义算子名称、输入、输出等信息，可以类比为定义一个 C 语言函数的声明，包括：函数名、入参及返回值类型等信息。
   > 例如本样例 `msopgen_demo.json` 中定义了算子的名称、输入输出变量的名称、类型和数据排布格式。
   > 算子函数的声明代码统一由工具生成，即生成一个空函数（只包含函数名、入参和返回值），函数体需要用户根据实际需求实现。

2. 生成算子代码框架

    执行以下命令生成 Ascend C 算子工程，参数说明：`-lan cpp` 指定生成 Ascend C 代码；`-c` 为芯片 SoC 型号：

   ```bash
    msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
   ```

   回显 `Generation completed`  表示执行成功。如需了解上述命令各参数的详细含义，请参阅 [msOpGen 代码仓库](https://gitcode.com/Ascend/msopgen) 的《使用指南》。

    >[!CAUTION]注意          
    > 上述命令生成的代码框架中，具体算子的实现为空，无法正常执行加法运算，需按照 [2.3.2 节](#232-实现核心逻辑) 内容进行修改后方可正常运行。 
   
3. 查看生成的结果

    > [!NOTE]说明   
    > 
    > **知识点（可选阅读）：关键概念**       
    > Host 侧：运行于 CPU 的代码，负责数据预处理、任务调度及算子调用。   
    > Kernel 侧：运行于 NPU 的代码，负责执行实际的大规模并行计算逻辑。   
    > Tiling：将大规模数据分块处理，以提高 Local Memory 利用率并优化内存访问效率。

    以下为部分生成结果文件的示例，生成的工程结构看起来庞大而复杂，但我们**仅需关注标记为【用户扩展点】的三个 C++ 文件**，其余均为框架代码，无特殊需求无需查看修改：

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

实际开发流程中，用户需在上述三个【用户扩展点】文件中自行实现具体算法逻辑。本教程可执行如下命令，复制使用已发布的加法教学进行演示体验：

```bash
cd ~/ot_demo/workspace/src/AddCustom/
bash ~/ot_demo/msot/example/quick_start/scripts/prepare_add_demo.sh --project .
```

输出 `Prepare sample script successful` 表示执行成功。
> [!NOTE]说明   
> 
> **知识点（可选阅读）：算子核心代码文件实现原理**  
> op_host/add_custom.cpp：实现 Host 侧的 Tiling 计算逻辑与算子原型注册。  
> op_kernel/add_custom_tiling.h：定义 Tiling 分块策略的数据结构。  
> op_kernel/add_custom.cpp：实现 Kernel 侧加法算子的具体计算逻辑（GM→UB→向量加法→UB→GM）。   
> 若需深入理解上述三个文件的功能与协作机制，除参考代码注释外，可阅读<a href="https://www.hiascend.com/developer/blog/details/0239124507827469022" target="_blank">《昇腾 Ascend C 编程入门教程（纯干货）》</a>。  

#### 2.3.3 编译与部署算子

1. 编译算子

    执行构建脚本，成功后将在 `build_out` 目录下生成 `.run` 格式的算子部署包：

    ```bash
    bash ./build.sh
    ```

2. 部署算子  
    执行如下命令部署算子：

    ```bash
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

    >[!NOTE]说明   
    > 
    > **知识点：什么是部署算子**  
    > 部署算子是指将算子注册到 CANN 框架中，本质上是将算子的二进制文件拷贝至系统公共目录，使其他程序能够通过标准接口（如 CANN API 或 PyTorch 等）自动发现并调用该算子。`*.run` 的部署包格式可以理解为一种自解压的压缩包。
3. 加入动态库路径
   
    部署成功后，按终端提示追加算子依赖的动态库路径：

    ```bash
    export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH
    ```

#### 2.3.4 验证算子功能

> [!CAUTION]注意   
> **关于 NPU 设备选择的说明**   
> 执行以下 `run.sh` 脚本会实际运行算子。脚本默认根据 `npu-smi info` 的查询结果，按显示顺序选择第一张空闲的 NPU 卡执行任务。
> 如需指定 NPU 卡，请根据 `npu-smi info` 返回的设备信息，使用其顺序号（取值范围为 [0, NPU 数量 - 1]）调用，例如：`bash ./run.sh 2`。

执行算子调用工程，验证算子功能（本例执行 1.0 + 2.0，预期结果为 3.0）：

```bash
cd ~/ot_demo/workspace/src/caller
bash ./run.sh
```

若输出如下内容，结果为 3.0，则表明算子已成功加载并计算正确：

```text
result is:
3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 
test pass
```

若出现如下错误信息，可参照下表排查确认：

```text
aclrtSetDevice failed. ERROR: xxxxxx
Init acl failed. ERROR: 1
```

| 现象 | 可能原因 | 处理方式 |
|------|----------|----------|
| 超过 30 秒无返回 | NPU 卡繁忙 | 按 Ctrl+C 终止，切换至其他空闲卡重试（指定方法见上文“关于 NPU 设备选择的说明”） |
| 出现如下 ACL 报错 | NPU 卡异常（硬件故障、驱动问题等）；<br>`/dev/hisi_hdc` 设备异常，比如未挂载、无权限等；<br>内存等系统资源不足 | 解决 NPU 卡故障或更换为正常卡后重试；错误码含义参见 [《ACL 错误码表》](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/850/API/appdevgapi/aclcppdevg_03_1345.html) |

### 2.4【检测】算子异常检测（msSanitizer）

算子开发完成后，可借助 msSanitizer 工具检测是否存在内存越界、竞争条件、未初始化变量或同步异常等严重运行时缺陷，从而高效定位潜在的错误：

#### 2.4.1 准备检测选项与源码

在 Kernel 侧 `CMakeLists.txt` 首行配置 `-sanitizer` 以启用检测插桩，并指定 `--fixture oob` 构造含越界访问的教学源码：

```bash
cd ~/ot_demo/workspace/src/AddCustom
bash ~/ot_demo/msot/example/quick_start/scripts/prepare_mode.sh --project . --mode sanitizer --fixture oob
```

输出 `Successfully prepared sanitizer mode` 表示检测模式准备成功。
>[!NOTE]说明  
> 构造异常如下：将 op_kernel/add_custom.cpp 中 `AscendC::DataCopy` 函数调用中的读取长度修改为 2 倍（`2 * this->tileLength`），导致访问超出 GM 内存中 `xGm` 的分配范围，从而触发“非法读取”错误。

#### 2.4.2 重新编译部署

```bash
bash ./build.sh
bash ./build_out/custom_opp_openEuler_aarch64.run
```

#### 2.4.3 执行内存检测

```bash
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck -- bash run.sh
```

若工具输出如下错误报告，则表明已成功执行，并识别到构造的越界访问（不同版本的显示可能会稍有不同，不影响学习工具使用）：  

1. illegal read of size 224：表示非法读取了 224 字节。   
2. op_kernel/add_custom.cpp:44:9：表明越界访问发生在 add_custom.cpp 第 44 行。

```output
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
> 算子出现内存问题后仍可能执行成功，这正体现了该工具的价值：内存问题通常具有偶发性，在多数情况下即使存在内存异常，程序仍可正常运行，表现为静默故障（Silent Failure），仅当问题累积至临界点时才会突发崩溃，难以通过表象直接定位。

#### 2.4.4 恢复正常样例

执行如下命令恢复演示样例源码和 Kernel CMake，已部署算子不变，下一节需重新显式重新构建与部署：

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/restore_demo.sh --project ~/ot_demo/workspace/src/AddCustom
```

回显 `Successfully restored source files` 表示执行成功。

### 2.5【调试】断点调试算子代码（msDebug）

若算子功能异常，可借助 msDebug 工具进行断点调试，高效定位问题：

#### 2.5.1 开启内核调试开关

确认内核调试开关 `debug_switch` 是否打开：

```bash
cat /proc/debug_switch
```

若输出值不为 1，请新开一个**宿主机终端**，使用 root 权限执行以下命令：

```bash
echo 1 > /proc/debug_switch
cat /proc/debug_switch
```

若 `cat /proc/debug_switch` 输出 `1`，表示设置成功；如果不能成功设置为 `1`，msDebug 功能不可用，只能跳过本节 msDebug 体验。

>[!CAUTION]注意    
> /proc/debug_switch 是昇腾驱动提供的 NPU 调试开关接口，用于控制是否允许 msDebug 调试运行在 NPU 上的算子 Kernel，是 /proc 下的虚拟文件。
> 由于容器的挂载方式和权限限制可能影响对驱动调试开关的访问与设置，因此需要由管理员用户在宿主机上操作并确认状态，否则可能在调试期间返回错误（如 `'A' packet returned an error: 8`）。  

#### 2.5.2 修改编译选项并重新部署

1. 修改编译选项

    准备调试模式：在 Kernel 侧 `CMakeLists.txt` 首行配置 `-g -O0`，启用调试信息、禁用编译优化。

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    bash ~/ot_demo/msot/example/quick_start/scripts/prepare_mode.sh --project . --mode debug
    ```

      回显 `Successfully prepared debug mode` 表示执行成功。

2. 重新编译部署算子

    ```bash
    bash ./build.sh
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

#### 2.5.3 设置调试环境变量

通过脚本设置 `LAUNCH_KERNEL_PATH`，指定算子 obj 加载路径并导入调试符号信息：

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
   
    待 `(msdebug)` 提示符出现后，执行如下命令，在 `add_custom.cpp` 第 34 行设置断点：

    ```text
    b add_custom.cpp:34
    ```

    回显 `Breakpoint 1: XXX` 表示设置成功。

    > [!CAUTION]
    >
    > 若此前未在宿主机正确启用 `/proc/debug_switch`，执行上述断点设置将触发警告，而在后续步骤运行 `run` 命令时将触发调试器错误（例如 `'A' packet returned an error: 8`），表明 msDebug 无法正常工作。

3. 运行算子
   
    执行如下命令启动程序并等待命中断点：

    ```text
    run
    ```

    显示如下信息，则表示成功命中断点（不同版本的显示可能会稍有不同，不影响学习工具使用）：

    ```output
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

#### 2.5.5 恢复调试准备

执行如下命令恢复演示样例源码和 Kernel CMake，已部署算子不变，下一节需重新显式重新构建与部署：

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/restore_demo.sh --project ~/ot_demo/workspace/src/AddCustom
```

回显 `Successfully restored source files` 表示执行成功。

### 2.6【调优】分析算子性能（msOpProf）

若算子性能未达预期，可借助 msOpProf 工具采集运行时性能数据，进行深入分析与优化，确保算子在不同昇腾硬件平台上高效执行。

#### 2.6.1 修改编译选项并重新编译部署

1. 修改编译选项
   
    准备调优模式：在 Kernel 侧 `CMakeLists.txt` 首行配置 `-g`，开启符号信息，保留工程原有优化策略：

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    bash ~/ot_demo/msot/example/quick_start/scripts/prepare_mode.sh --project . --mode profile
    ```

    回显 `Successfully prepared profile mode` 表示执行成功。
    > [!NOTE]说明   
    > 
    > **知识点（可选阅读）：为什么不同工具会设置不同 -O 优化等级**   
    > -O0 会关闭大部分编译优化，使调试时的执行过程更接近源码结构，便于设置断点、单步执行和查看变量；调试符号信息还需通过 -g 生成。
    > -O2 会启用更多编译优化。在调试器中单步执行时，可能出现源码跳行、多行对应同一执行位置或函数被内联等现象，其与 -O0 的性能可能存在数倍差异。性能分析应使用与正式部署版本一致的优化配置，通常为 -O2 或工程默认的优化配置，避免沿用调试模式的 -O0，导致采集结果偏离实际运行性能。

2. 重新编译部署算子

    ```bash
    bash ./build.sh
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

#### 2.6.2 启动真机与仿真采集

> [!NOTE]说明   
> **知识点：仿真和上板采集信息的区别**   
> 仿真：可在不依赖算力卡设备的条件对指令流追踪、代码热点定位等方面进行稳定初步的分析，但对内存访问延迟、带宽瓶颈等硬件相关行为的模拟精度有限。  
> 上板：通过在实际设备上运行，可精确捕获算子运行耗时、各 Pipe 使用情况、内存带宽、Cache 行为等真实硬件特性。  
> 实际开发中建议两种方式结合，已实现高效全面性能诊断。

1. 仿真器性能采集

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msopprof simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msopprof_output_sim ./execute_add_op
    ```
    
    回显 `Op profiling finish.` 表示采集成功，采集结果见回显日志中 `Profiling results saved in: xxx` 路径。
2. 上板性能采集 

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msopprof --output=./msopprof_output_npu ./execute_add_op
    ```

    回显 `Op profiling finish.` 表示采集成功，采集结果见回显日志中 `Profiling results saved in: xxx` 路径。

#### 2.6.3 查看性能数据结果

工具在指定 `--output` 目录下生成 `.csv` 和 `.bin` 格式的结果文件：

- CSV 文件

    例如 `MemoryUB.csv`，打开可以看到如下信息：

    数据显示任务被均分为 8 个 block，全部调度至 Vector Core 执行。例如 Block 0 的带宽（1.02 GB/s）明显高于 Block 1（0.77 GB/s），如果差异过大，可能提示存在优化空间：

    | block_id | sub_block_id | aiv_time(μs) | aiv_total_cycles | aiv_ub_read_bw_vector(GB/s) | aiv_ub_write_bw_vector(GB/s) |
    |:--------:|:------------:|:------------:|:----------------:|:---------------------------:|:----------------------------:|
    |    0     |   vector0    |  7.456666  |      13422      |          1.023164           |           0.511582           |
    |    1     |   vector0    |  9.914444  |      17846      |          0.769523           |           0.384762           |
    |    2     |   vector0    |  10.001111 |      18002      |          0.762855           |           0.381427           |
    |    3     |   vector0    |  9.684444  |      17432      |          0.787799           |           0.393899           |
    |    4     |   vector0    |  9.747222  |      17545      |          0.782725           |           0.391363           |
    |    5     |   vector0    |  9.062222  |      16312      |          0.84189            |           0.420945           |
    |    6     |   vector0    |  9.293889  |      16729      |          0.820904           |           0.410452           |
    |    7     |   vector0    |  8.658889  |      15586      |          0.881105           |           0.440553           |

- BIN 文件

    可使用 `MindStudio Insight` 工具打开，以图形化方式直观展示各类性能视图，例如：计算内存热力图、Cache 热力图以及算子代码热点图等。

    > [!NOTE]
    >
    > 若想体验可视化的图表查看，请参考 <a href="https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/install_guide/mindstudio_insight_install_guide.md" target="_blank">《MindStudio Insight 工具文档》</a>安装 Insight 工具。

#### 2.6.4 恢复调优准备

恢复演示源码配置；已部署算子和采集结果不变。若要使用恢复后的正常算子，需进行显式构建与部署：

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/restore_demo.sh --project ~/ot_demo/workspace/src/AddCustom
```

回显 `Successfully restored source files` 表示执行成功。

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

本教程仅覆盖了各工具的入门用法，每个工具都提供了更丰富的高级能力，建议按需访问对应仓库的《使用指南》等深入学习：

| 工具 | 高级能力说明 |
|------|--------------|
| [msKPP](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/user_guide/mskpp_user_guide.md) | 使用 Cache 命中率、随路转换等建模、多种 Tiling 方案的性能对比分析等。 |
| [msOpGen](https://gitcode.com/Ascend/msopgen/blob/master/docs/zh/user_guide/msopgen_user_guide.md) | 复杂算子模板定制、多输入多输出算子的工程生成等。 |
| [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/master/docs/zh/user_guide/mssanitizer_user_guide.md) | 竞争条件检测、同步异常诊断、未初始化变量检查等更多检测模式。 |
| [msDebug](https://gitcode.com/Ascend/msdebug/blob/master/docs/zh/user_guide/msdebug_user_guide.md) | 内存查看、核切换、解析 Core dump 文件等高级调试技巧。 |
| [msOpProf](https://gitcode.com/Ascend/msopprof/blob/master/docs/zh/user_guide/msopprof_user_guide.md) | 结合 [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/master/docs/zh/install_guide/mindstudio_insight_install_guide.md) 进行可视化性能分析，包括计算内存热力图、Cache 热力图及代码热点图。 |

**第三步：落地真实业务 —— 从教学走向生产**  

深入研读 [《Ascend C 编程指南（官方教程）》](https://www.hiascend.com/zh/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll)，系统掌握多级流水、数据排布、内存管理等核心概念，在此基础上尝试将工具链应用于实际业务算子的开发与调优，逐步构建从原型验证到生产级交付的完整能力。

## 3. FAQ

### 3.1 编译调用算子程序时报错：fatal error: aclnn_add_custom.h: No such file or directory

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

### 3.2 执行 execute_add_op 时异常报错：undefined symbol: aclnnAddCustomGetWorkspaceSize

**问题现象**

```text
execute_add_op: symbol lookup error: ./build/execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize
```

**问题原因** 

部署完算子后，没有按输出提示将 `.so` 加入环境变量 `LD_LIBRARY_PATH` 中。

**解决方法** 

按 [2.3.3 编译与部署算子](#233-编译与部署算子) 第 3 步，重新设置 `LD_LIBRARY_PATH` 环境变量。

### 3.3 执行 msDebug 设置断点时报错：WARNING:  Unable to resolve breakpoint to any actual locations

**问题现象**

```text
(msdebug) b add_custom.cpp:23
Breakpoint 1: no locations (pending on future shared library load).
WARNING:  Unable to resolve breakpoint to any actual locations.
```

**问题原因** 

指定的断点行可能是空行或注释等无法设置断点的行，或者 `/proc/debug_switch` 没有成功设置，原因参考下节说明。

**解决方法** 

查看代码源文件，确认代码的真实行号；按 [2.5.1 开启内核调试开关](#251-开启内核调试开关) 以 root 权限在宿主机上（注意不是容器内）设置 `/proc/debug_switch` = 1。如果不能设置成功，只能跳过此工具体验。

### 3.4 执行 msDebug 的 run 时报错：error: 'A' packet returned an error: 8

**问题现象**

```text
error: 'A' packet returned an error: 8
```

**问题原因** 

该错误表示调试启动请求失败，可能与 `/proc/debug_switch` 未开启、设备访问受限或驱动与调试组件不兼容等因素有关。

**解决方法** 

容器的挂载方式和权限限制可能影响对 `/proc/debug_switch` 的访问与设置，建议由管理员用户在宿主机上操作，并确认开关状态为 `1`。若开关已开启但调试仍失败，需结合相关日志进一步检查设备访问权限及驱动、调试组件的兼容性。
