# Operator Development Toolchain Quick Start

<br>

## 1. Overview

The MindStudio operator development toolchain includes a variety of tools. This document uses the development of a simple addition operator as an example to guide you through the entire operator development process, allowing you to intuitively experience the efficiency and convenience brought by the toolchain.

**Experience Map (Core operations take only 10 minutes, and can be executed quickly with Copy/Paste throughout)**     
> **Recommended Procedure**: Step 1 is the foundation; after completing Step 1, you can experience Step 2 or Step 3; Steps 4, 5, and 6 all depend on the project generated in Step 3, but these three are independent of each other and can be learned as needed.

 | Step | Phase | Core Tools | Measured Operation Time | Recommended Theory Learning |
 | :---: | :---: | :--- | :---: | :---: |
 | **1** | **Environment Preparation** | CANN container image | 3 minutes | 5 minutes |
 | **2** | **Operator Design** | msKPP | 30 seconds | 5 minutes |
 | **3** | **Project Development** | msOpGen | 1 minute | 20 minutes |
 | **4** | **Anomaly Detection** | msSanitizer | 1 minute | 10 minutes |
 | **5** | **Native Debugging** | msDebug | 1 minute | 10 minutes |
 | **6** | **Performance Tuning** | msOpProf | 1 minute | 10 minutes |

## 2. Procedure

### 2.1 [Environment] Essential Environment Preparation (Mandatory Prerequisite)

🛑 **This section is a mandatory prerequisite. Skipping it will cause many subsequent operations to fail.**
This tutorial **supports only** standardized CANN container environments. Bare-metal, virtual machine, or other non-standard container deployments are not supported.

#### 2.1.1 Installing the CANN Container Environment

**Complete the environment installation strictly according to the following guide:**  
👉 **[Ascend AI Operator Development Toolchain Learning Environment Installation Guide](installation_guide.md)**

> **Estimated time for an environment with public network access: about 3 minutes (the exact time depends on network conditions)**  
> After the installation is complete, you will obtain a standardized container environment with all operator tools, sample code, and dependent libraries preinstalled.

#### 2.1.2 Running the Environment Self-Check Script (Must Pass)

Before the hands-on experience, **copy the entire script that follows**, paste it into the terminal in the container, and run it. You can continue only when all output shows `[PASS]`. Otherwise, return to the preceding section and prepare the environment strictly as required:

```bash
# 1. Container environment check
[ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ] && echo -e "\033[32m[PASS] CANN container environment OK \033[0m" || echo -e '\033[31m[FAIL] Non-standard container or not inside the container!\033[0m'
# 2. Chip model variable check
[ -n "$MY_STUDY_VAR_CHIP_SOC_TYPE" ] && echo -e "\033[32m[PASS] Chip Soc type: $MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m" || echo -e "\033[31m[FAIL] Missing environment variable \$MY_STUDY_VAR_CHIP_SOC_TYPE\033[0m"
# 3. Sample code repository check
[ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] Example code repository OK\033[0m" || echo -e "\033[31m[FAIL] Code repository missing\033[0m"
# 4. Core tool command check
command -v msopgen >/dev/null && echo -e "\033[32m[PASS] msopgen command OK\033[0m" || echo -e "\033[31m[FAIL] msopgen command missing\033[0m"
command -v mssanitizer >/dev/null && echo -e "\033[32m[PASS] mssanitizer command OK\033[0m" || echo -e "\033[31m[FAIL] mssanitizer command missing\033[0m"
command -v msdebug >/dev/null && echo -e "\033[32m[PASS] msdebug command OK\033[0m" || echo -e "\033[31m[FAIL] msdebug command missing\033[0m"
command -v msopprof >/dev/null && echo -e "\033[32m[PASS] msopprof command OK\033[0m" || echo -e "\033[31m[FAIL] msopprof command missing\033[0m"
```

🚀 **All subsequent experience phases are executed in the container and fully support fast Copy/Paste execution. Follow all the steps in each section in order. Do not skip or reorder the steps.**

### 2.2 [Design] Operator Modeling Design (msKPP)

First, design the operator algorithm. With the msKPP tool, you can obtain operator performance modeling results in seconds, estimate performance without hardware, and quickly verify the feasibility of the implementation plan. Follow the steps to experience the effect first; the principles can be read later:

> [!NOTE] Note   
> 
> **msKPP Tool Principles**   
> msKPP is not a traditional executable program but a dedicated Python class library for Ascend. Users need to `import` relevant modules, write and execute Python scripts, and generate performance analysis result files to complete the modeling. The internal principle involves pre-collecting performance data of various instruction operations in real environments, and modeling and estimating various performance overheads based on the user-defined operator execution flow.

#### 2.2.1 Checking the Environment

This tool **supports only the Ascend 910B** series of chips. Run the following command:

```bash
chip=$(npu-smi info -m 2>/dev/null | grep -oP 'Ascend\s*\S+' | head -1); case "$chip" in 'Ascend 910B'* ) echo -e "\n\e[32m[PASS] Chip SoC type [$chip] check passed. Please continue with the experience.\e[0m";; * ) echo -e "\n\033[31m[FAIL] Get chip: ${chip:-None}. The current environment does not support this tool. Please skip this experience.\033[0m" >&2;; esac
```

If the output is `[PASS]`, continue the experience. If the output is `[FAIL]`, switch to an environment with an Ascend 910B chip before continuing the experience. If you cannot switch for now, skip this section.

#### 2.2.2 Writing a Python Modeling Script

1. Create a sub-workspace directory

    ```bash
    mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
    ```

2. Develop the Python script

    > [!NOTE] Note  
    > 
    > **msKPP Domain-Specific Language (DSL) Solution**   
    > This set of libraries and interfaces is a "dialect" specifically designed for Ascend performance modeling. It requires dedicated learning to master and cannot be written directly using only general Python syntax. However, its usage is relatively simple and can be applied after a brief study.
    > Standard development process: You must first import `Tensor`, `Chip`, and the instructions necessary for operator implementation (for example, `vadd`). Use the `with` statement to enter the context of the operator implementation code, and then create Tensors to perform specific operations. The sample script contains detailed comments. For descriptions of other instruction interfaces, refer to the [msKPP Tool Interface Description](https://gitcode.com/Ascend/mskpp/blob/26.1.0/docs/en/api_reference/mskpp_api_reference.md).

    As this is a quick start, copying the prepared msKPP DSL script here is considered development completion (this tutorial focuses on toolchain usage; actual development requires you to implement it yourself):

    ```bash
    \cp -f ~/ot_demo/msot/example/quick_start/mskpp/mskpp_demo.py ./
    ```

#### 2.2.3 Executing Performance Modeling

Run the Python script to start performance modeling. If the execution succeeds, a result directory named `MSKPP{timestamp}` is automatically generated in the current directory:

```bash
python3 mskpp_demo.py
```

If the script reports an error indicating `Chip is unsupported`, the possible causes are as follows:

1. **Hardware incompatibility**: Confirm whether the current chip model is of the 910B series (you can obtain it with the `npu-smi info` command). This tool supports only 910B series chips. Switch to an environment with 910B series chips before proceeding.  
2. **Environment variable not configured**: Check whether the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` is correctly set. If the variable is empty, refer to Section 5 of the [Operator Development Toolchain Learning Environment Installation Guide](./installation_guide.md#5-in-the-container-setting-the-chip-soc-model) to reconfigure it.

#### 2.2.4 Viewing Modeling Results

The following are examples of some generated result files:

```text
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

Taking `Instruction_statistic.csv` as an example, its content is as follows:

| Instruction  | Duration (µs) | Cycle | Size(B) | Ops  |
|:--------------:|:--------------:|:-------:|:---------:|:------:|
| MOV-GM_TO_UB |    0.3081    |  570  |  6144   |  -   |
|     VADD     |    0.0135    |  25   |    -    | 1536 |
| MOV-UB_TO_GM |    0.4254    |  787  |  3072   |  -   |

From the above content, it can be seen that MOV-UB_TO_GM (moving from UB to GM) has the longest duration and the highest number of instruction cycles, making it the critical path that requires focused attention during performance optimization. In actual development, if such memory transfer time is found to account for an excessively high proportion, priority should be given to optimizing data reuse (Tiling) or using more efficient transfer instructions.

### 2.3 [Development] Building the Operator Project (msOpGen)

After the algorithm design is complete, you can proceed to the operator code writing phase. Operator projects are relatively complex and contain a large amount of framework code. The msOpGen tool can automatically generate a complete operator project framework, allowing developers to focus on core algorithm implementation and avoid wasting time on repetitive tasks such as project setup and compilation configuration. Follow the operations first to experience the effect; the theory section can be read later:

#### 2.3.1 Generating Project Framework

1. Create a sub-workspace directory.

    Create a subdirectory named `src` as the root directory for the operator source code. All subsequent source code operations will be based on this path:

    ```bash
    mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src/
    ```

2. Develop the operator definition configuration file.

    > [!NOTE] Note   
    > 
    > **Key Point (Optional Reading): msOpGen Input Configuration File**   
    > A custom-format JSON configuration file, which can be simply analogized to defining a C function declaration, including the function name, input parameters, and return value type information.
    > For example, `msopgen_demo.json` defines the name of the operator, the names, types, and data layout formats of its input and output variables.
    > The operator function declaration code is uniformly generated by the tool, which produces an empty function (with only the function name, input parameters, and return value). The function body needs to be implemented by the user.

    As this is a quick start guide, copying the prepared configuration file here is considered development complete (this tutorial focuses on toolchain usage; actual development requires you to implement it yourself):

    ```bash
    \cp -f ~/ot_demo/msot/example/quick_start/msopgen/msopgen_demo.json ./
    ```

3. Generate code framework based on configuration.

    Run the following command to generate an Ascend C operator project. Parameter description: `-lan cpp` indicates that Ascend C code is to be generated. `-c` specifies the chip SoC model (processing may differ across different chips):

    ```bash
    msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
    ```

    >[!CAUTION] Note          
    > In the code framework generated by the preceding command, the implementation of the specific operator is empty and cannot perform addition normally. You must modify it as described in [2.3.2 Implementing Core Logic](#232-implementing-core-logic) before it can run correctly. 

    For detailed explanations of the parameters in the preceding command, refer to the *User Guide* of the [msOpGen code repository](https://gitcode.com/Ascend/msopgen).

4. View generated results.

    > [!NOTE] Note   
    > 
    > **Key Point (Optional Reading): Key Concepts**       
    > Host Side: Code running on the CPU, responsible for data preprocessing, task scheduling, and operator invocation.   
    > Kernel Side: Code running on the NPU, responsible for executing the actual large-scale parallel computation logic.   
    > Tiling: Partitioning large-scale data into blocks to improve Local Memory utilization and optimize memory access efficiency.

The generated project structure may appear large and complex, but we **only need to focus on the three C++ files marked as [User Extension Points]**. The rest are framework code, which do not need to be viewed or modified unless there are special requirements:

    ```text
    AddCustom
    ├── build.sh                 // Build entry script
    ├── CMakeLists.txt           // CMakeLists.txt of the operator project
    ├── framework                // Directory for operator plug-in implementation files. The generation of a single-operator model file does not depend on operator adaptation plug-ins and does not require attention
    │   ├── CMakeLists.txt
    │   └── tf_plugin
    ├── op_host                  // Host-side implementation files
    │   ├── add_custom.cpp       // [User extension point] File for operator prototype registration, shape derivation, information library, tiling implementation, and other content
    │   └── CMakeLists.txt
    ├── op_kernel                // Kernel-side implementation files
    │   ├── add_custom.cpp       // [User extension point] Operator code implementation file
    │   ├── add_custom_tiling.h  // [User extension point] Operator tiling definition file
    │   └── CMakeLists.txt
    └── CMakePresets.json        // Compilation configuration
    ```

#### 2.3.2 Implementing Core Logic

> [!NOTE] Note   
> 
> **Key Point (Optional Reading): Implementation Principles of Operator Kernel Code Files**  
> `op_host/add_custom.cpp`: Implements the Tiling computation logic on the Host side and operator prototype registration.  
> `op_kernel/add_custom_tiling.h`: Defines the data structure for the Tiling strategy.  
> `op_kernel/add_custom.cpp`: Implements the specific computation logic of the addition operator on the Kernel side (GM→UB→vector addition→UB→GM).   
> If you need a deeper understanding of the functions and collaboration mechanisms of the three aforementioned files, in addition to referring to the code comments, you are advised to read the <a href="https://www.hiascend.com/developer/blog/details/0239124507827469022" target="_blank">Ascend C Programming Introductory Tutorial (Pure Practical Information)</a> in detail.  
> The `keep_soc_info.py` script works as follows: it automatically obtains the SoC chip type information of the current environment and refreshes it into the C++ files.

Implement the specific algorithm logic in the three [User Extension Point] files mentioned above. As this is a quick start, copying the three prepared C++ files here is considered development completion (this tutorial focuses on toolchain usage; actual development requires implementing the core logic yourself):

```bash
cd ~/ot_demo/workspace/src/AddCustom/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py get ./op_host/add_custom.cpp # Obtain the SoC information of the current environment
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom.cpp ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom_tiling.h ./op_kernel/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ./op_kernel/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py set ./op_host/add_custom.cpp # Refresh the SoC information in the code to that of the current environment
```

#### 2.3.3 Compiling and Deploying Operators

1. Compile the operator.

    Run the build script. Upon success, an operator deployment package in `.run` format will be generated in the `build_out` directory:

    ```bash
    bash ./build.sh
    ```

2. Deploy the operator.

    >[!NOTE] Note   
    > 
    > **Key Point: What Is Deploying Operators**  
    > Deploying operators refers to registering the operator with the CANN framework. Essentially, it involves copying the binary files of the operator to a system public directory, allowing other programs to automatically discover and invoke the operator through standard interfaces (such as CANN API or PyTorch). The `*.run` deployment package format can be simply understood as a self-extracting archive.

    Run the following command to deploy the operator:

    ```bash
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

3. Add the dynamic library path.

    After successful deployment, append the dynamic library path that the operator depends on as prompted by the terminal:

    ```bash
    export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH
    ```

#### 2.3.4 Verifying Operator Functionality

> [!CAUTION] Note   
> **Notes on NPU Device Selection**   
> Executing the following `run.sh` script will actually run the operator and will randomly select an idle NPU to execute the task.
> If you want to specify an NPU for execution, use the NPU information returned by the `npu-smi info` command and invoke it with its sequence number (value range: [0, number of NPUs - 1]) as follows: `bash ./run.sh 2`

Execute the operator invocation project to verify the operator functionality (this example executes 1.0 + 2.0, with an expected result of 3.0):

```bash
\cp -rf ~/ot_demo/msot/example/quick_start/msopgen/caller ~/ot_demo/workspace/src/
cd ~/ot_demo/workspace/src/caller
bash ./run.sh
```

If the following content is output and the result is 3.0, it indicates that the operator has been successfully loaded and calculated correctly:

```text
result is:
3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 
test pass
```

If you do not see the preceding output, troubleshoot according to the following table:

| Symptom | Possible Cause | Handling |
|------|----------|----------|
| No result for more than 30 seconds | The NPU is busy | Press Ctrl+C to terminate, switch to another idle NPU, and retry (see "Notes on NPU Device Selection" for how to specify an NPU). |
| The following ACL error appears | The NPU is abnormal (hardware fault, driver issue, and so on).<br>`/dev/hisi_hdc` device abnormality, for example, not mounted or no permission.<br>Insufficient system resources such as memory. | Resolve the NPU fault or switch to a normal NPU and then retry. See [ACL Error Code Table](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/850/API/appdevgapi/aclcppdevg_03_1345.html) for the meaning of the error codes. |

```text
aclrtSetDevice failed. ERROR: xxxxxx
Init acl failed. ERROR: 1
```

#### 2.3.5 Backing Up the Kernel-Side `CMakeLists.txt`

The execution of the subsequent three tools requires modification of this `CMakeLists.txt`. Keep this backup for restoring the environment:

```bash
\cp ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak
```

### 2.4 [Detection] Operator Anomaly Detection (msSanitizer)

After the operator development is complete, you can use the msSanitizer tool to detect serious runtime defects such as memory out-of-bounds, race conditions, uninitialized variables, or synchronization anomalies, thereby efficiently locating potential hidden errors. Follow the operation to experience the effect first; the principle part can be read later:

#### 2.4.1 Modifying Compilation Options

To enable the detection capability, you need to insert the sanitizer compilation option at the first line of the `CMakeLists.txt` on the Kernel side to inject detection stub code:

```bash
cd ~/ot_demo/workspace/src/AddCustom
sed -i '1i npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)' op_kernel/CMakeLists.txt
```

#### 2.4.2 Constructing a Memory Out-of-Bounds Error

Overwrite the original implementation with the prepared source file containing defective code to **artificially introduce an out-of-bounds access**:

```bash
\cp -f ~/ot_demo/msot/example/quick_start/mssanitizer/bug_code/add_custom.cpp op_kernel/add_custom.cpp
```

>[!NOTE] Note  
> The key modification is as follows: the read length in the `AscendC::DataCopy` function call is changed to twice the original (`2 * this->tileLength`), causing the access to exceed the allocation range of `xGm` in GM memory, thereby triggering an "illegal read" error.

#### 2.4.3 Recompiling and Deploying

```bash
bash ./build.sh
bash ./build_out/custom_opp_openEuler_aarch64.run
```

#### 2.4.4 Executing Memory Sanitization

```bash
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck -- bash run.sh
```

If the tool outputs the following error report, it indicates successful execution and that the constructed out-of-bounds access has been identified (the display may vary slightly between versions, which does not affect learning how to use the tool):  

1. `illegal read of size 224`: Indicates an illegal read of 224 bytes.   
2. `op_kernel/add_custom.cpp:44:9`: Indicates that the out-of-bounds access occurred at line 44 of `add_custom.cpp`.   

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

> [!NOTE] Note  
> The operator may still execute successfully even with memory issues, which is exactly where the value of this tool lies: memory problems are usually intermittent. In most cases, even when memory anomalies exist, the program still runs normally. Only when the problem accumulates to a critical point does a sudden crash occur, making it difficult to locate the issue directly from the surface.

#### 2.4.5 Reverting Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```bash
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ~/ot_demo/workspace/src/AddCustom/op_kernel/
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.5 [Debugging] Breakpoint Debugging of Operator Code (msDebug)

If the operator functions abnormally, you can use the msDebug tool for breakpoint debugging to efficiently locate issues. Follow the steps to experience the effect first; the principles can be read later:

#### 2.5.1 Enabling Kernel Debug Switch

>[!CAUTION] Note    
> **msDebug requires the kernel debug switch `/proc/debug_switch` to be enabled with root privileges**  
> 
> The switch is disabled by default and can be modified only by root. msDebug works correctly only after the switch is enabled.  
> 
> **Operations in the container are usually ineffective:**  
> Even if you successfully write to `/proc/debug_switch` as root inside the container, because the host commonly virtualizes `/proc` through mechanisms such as copy-on-write (CoW), shadow files, or overlay mounts, the setting **affects only the container view** and does not actually take effect in the kernel. Therefore, even if `cat /proc/debug_switch` shows 1, msDebug may still be unavailable and may return errors during debugging (for example, `'A' packet returned an error: 8`).  
> 
> **Recommended Practice:**  
> If you are in a shared development machine, a common container, or an environment without host access, contact your system administrator for assistance in enabling it, or switch to a host environment with root privileges to experience this feature.

Check whether the kernel debug switch `debug_switch` is enabled:

```bash
cat /proc/debug_switch
```

If the output value is not 1, open a new **host terminal** and run the following command with root privileges. After the command completes, return to the current container terminal and continue with the subsequent steps:

```bash
echo 1 > /proc/debug_switch
cat /proc/debug_switch
```

If `cat /proc/debug_switch` outputs `1`, the setting was successful. If it cannot be successfully set to `1`, the msDebug function is unavailable, and you can only skip the msDebug experience in this section.

#### 2.5.2 Modifying Compilation Options and Redeploying

1. Modify compilation options.

    Insert the configuration at the first line of the Kernel-side `CMakeLists.txt` to enable debug information and disable compilation optimization:

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    sed -i '1i npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)' op_kernel/CMakeLists.txt
    ```

2. Recompile and deploy the operator.

    ```bash
    bash ./build.sh
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

#### 2.5.3 Setting Debug Environment Variables

Set `LAUNCH_KERNEL_PATH` through a script to specify the operator obj loading path and import debug symbol information:

```bash
source ~/ot_demo/msot/example/quick_start/msdebug/set_kernel_obj_env.sh
```

#### 2.5.4 Breakpoint Debugging and Variable Inspection

1. Start the debugger

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msdebug execute_add_op
    ```

2. Set breakpoint.

    After the `(msdebug)` prompt appears, set a breakpoint at line 34 of `add_custom.cpp`:

    ```text
    b add_custom.cpp:34
    ```

    >[!CAUTION] Note  
    > If `/proc/debug_switch` was not correctly enabled on the host machine beforehand, setting the breakpoint as described in the preceding step will trigger a warning, and running the `run` command in the subsequent steps will trigger a debugger error (for example, `'A' packet returned an error: 8`), indicating that msDebug cannot work properly.

3. Run the operator.

    Enter `run` to start the program and wait for the breakpoint to be hit:

    ```text
    run
    ```

    If the following information is displayed, the breakpoint has been hit successfully (the display may vary slightly between versions, which does not affect learning how to use the tool):

    ```text
    Process 2799 launched: '/root/ot_demo/workspace/src/caller/build/execute_add_op' (aarch64)
    Running on NPU [0]. If this is the first run on this NPU, scheduling may take a few seconds; please wait...
    [Launch of Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 on Device 0]
    1 location added to breakpoint 1
    Process 2799 stopped
    [Switching to focus on Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0, CoreId 35, Type aiv]
    * thread #1, name = 'execute_add_op', stop reason = breakpoint 1.2
        frame #0: 0x000012c0412008b4 device_debugdata_0`KernelAdd::Init(this=0x00000000002e7860, x=0x12c0c0015000, y=0x12c0c001e000, z=0x12c0c0027000, totalLength=16384, tileNum=8) (.vector) at add_custom.cpp:34:9
       31           this->tileLength = this->blockLength / this->tileNum / BUFFER_NUM;
       32  
       33           // Set up the global memory buffer and allocate the global shared memory region for the current AI Core
    -> 34           xGm.SetGlobalBuffer((__gm__ DTYPE_X *)x + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
       35           yGm.SetGlobalBuffer((__gm__ DTYPE_Y *)y + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
       36           zGm.SetGlobalBuffer((__gm__ DTYPE_Z *)z + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
    ```

4. View variable values.

    Execute the following command at the breakpoint to display all local variables in the current scope:

    ```text
    var
    ```

5. Exit the debugger.

    ```text
    q
    ```

#### 2.5.5 Reverting Manual Modifications

Prepare for subsequent tool usage by reverting manual modifications:

```bash
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.6 [Tuning] Analyzing Operator Performance (msOpProf)

If the operator performance does not meet expectations, you can use the msOpProf tool to collect runtime performance data for in-depth analysis and optimization, ensuring efficient execution of the operator on different Ascend hardware platforms. Follow the steps to experience the effect first; the principles can be read later:

#### 2.6.1 Modifying Compilation Options and Recompiling/Deploying

1. Modify compilation options.

    Insert a configuration line at the first line of the Kernel-side `CMakeLists.txt` to enable debug information:

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    sed -i '1i npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)' op_kernel/CMakeLists.txt
    ```

    > [!NOTE] Note   
    > 
    > **Key Point (Optional Reading): Why the `-O` optimization level is switched back and forth between tools**   
    > During the debugging phase, to support breakpoints and variable inspection, `-O0` must be used to disable optimization and preserve accurate symbol mapping. However, the performance gap between `-O0` and `-O2` can be several times. Therefore, performance analysis must be based on code compiled with `-O2` (or the default optimization level). Otherwise, the collected data will severely deviate from real-world scenarios and lose its reference value.

2. Recompile and deploy the operator.

    ```bash
    bash ./build.sh
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

#### 2.6.2 Starting On-Board and Simulation Collection

> [!NOTE] Note   
> **Differences Between On-Board and Simulation Collection Information**   
> On-board: Can accurately capture operator runtime, Pipe usage, memory bandwidth, cache behavior, and other real hardware characteristics, which are often key metrics that simulators struggle to reproduce with high fidelity.  
> Simulation: Provides more complete and stable analysis capabilities in areas such as instruction stream tracing and code hotspot localization, but has limited simulation accuracy for hardware-related behaviors like memory access latency and bandwidth bottlenecks.  
> Therefore, you are advised to combine both methods to complement each other's strengths for comprehensive performance diagnosis. If you do not have real hardware (NPU) in some scenarios, you can use simulation mode for preliminary performance estimation and hotspot analysis.

1. Perform on-board performance profiling.

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msopprof --output=./msopprof_output_npu ./execute_add_op
    ```

2. Perform simulator performance profiling.

    ```bash
    msopprof simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msopprof_output_sim ./execute_add_op
    ```

#### 2.6.3 Viewing Performance Data Results

The tool generates result files in `.csv` and `.bin` formats in the specified `--output` directory. If no errors are reported in the output, the execution is successful:

- CSV files   
For example, opening `MemoryUB.csv` reveals the following information:  
The data shows that the task is evenly divided into 8 blocks, all scheduled to the Vector Core for execution. For instance, the bandwidth of Block 0 (1.02 GB/s) is significantly higher than that of Block 1 (0.77 GB/s). If the difference is too large, it may indicate potential optimization opportunities:

  | block_id | sub_block_id | aiv_time(µs) | aiv_total_cycles | aiv_ub_read_bw_vector(GB/s) | aiv_ub_write_bw_vector(GB/s) | 
  |:--------:|:------------:|:------------:|:----------------:|:---------------------------:|:----------------------------:|
  |    0     |   vector0    |  7.456666  |      13422      |          1.023164           |           0.511582           | 
  |    1     |   vector0    |  9.914444  |      17846      |          0.769523           |           0.384762           | 
  |    2     |   vector0    |  10.001111 |      18002      |          0.762855           |           0.381427           | 
  |    3     |   vector0    |  9.684444  |      17432      |          0.787799           |           0.393899           | 
  |    4     |   vector0    |  9.747222  |      17545      |          0.782725           |           0.391363           | 
  |    5     |   vector0    |  9.062222  |      16312      |          0.84189            |           0.420945           | 
  |    6     |   vector0    |  9.293889  |      16729      |          0.820904           |           0.410452           | 
  |    7     |   vector0    |  8.658889  |      15586      |          0.881105           |           0.440553           | 

- BIN file   
It can be opened using the `MindStudio Insight` tool, which provides an intuitive graphical display of various performance views, such as: computation memory heatmaps, cache heatmaps, and operator code hotspot maps.

  > [!NOTE] Note  
  > 
  > To experience visual chart viewing, refer to the <a href="https://gitcode.com/Ascend/msinsight/blob/26.1.0/docs/zh/install_guide/mindstudio_insight_install_guide.md" target="_blank">MindStudio Insight Tool Documentation</a> to install the Insight tool.

#### 2.6.4 Reverting Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```bash
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.7 [Completion] Advanced Learning Path

Congratulations on completing the introductory experience of the Operator Development Toolchain.

At this point, you have fully walked through the entire operator development process of "Design → Develop → Detect → Debug → Tune" and have practically experienced the basic usage of the following five core tools:

| Tool | Core Capabilities You Have Mastered |
| ----------- | --------------------------------- |
| **msKPP** | Write DSL scripts for operator performance modeling and estimate performance bottlenecks without hardware. |
| **msOpGen** | Automatically generate operator project frameworks based on configuration files, and complete compilation, deployment, and functional verification. |
| **msSanitizer** | Inject detection stub code to locate the source code location of runtime defects such as memory out-of-bounds. |
| **msDebug** | Start breakpoint debugging, set breakpoints in NPU operator code, and inspect variables. |
| **msOpProf** | Collect performance data through both on-board and simulation modes, and analyze the execution efficiency of each Block. |

If you want to continue with advanced experience, you can refer to the following steps:

**Step 1: Consolidating the Foundation: Independently Developing a New Operator**  

Refer to the `AddCustom` example in this tutorial and try to independently implement a subtraction operator (`SubCustom`) or multiplication operator (`MulCustom`), focusing on: differences in Tiling strategy design, the use of different computation instructions (such as `vsub`, `vmul`), and the end-to-end compilation and deployment process.

**Step 2: Diving into Tools: Mastering the Advanced Features of Each Tool**  

This tutorial only covers the introductory usage of each tool. Each tool offers richer advanced capabilities. You are advised to access the *User Guide* of the corresponding repository as needed for in-depth learning:

| Tool | Advanced Capabilities |
|------|--------------|
| [msKPP](https://gitcode.com/Ascend/mskpp/blob/26.1.0/docs/en/user_guide/mskpp_user_guide.md) | Modeling using cache hit rate and in-line conversion, performance comparison analysis of multiple Tiling strategies, and so on. |
| [msOpGen](https://gitcode.com/Ascend/msopgen/blob/26.1.0/docs/en/user_guide/msopgen_user_guide.md) | Complex operator template customization, project generation for multi-input multi-output operators, and so on. |
| [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/26.1.0/docs/en/user_guide/mssanitizer_user_guide.md) | More detection modes such as race condition detection, synchronization anomaly diagnosis, and uninitialized variable checking. |
| [msDebug](https://gitcode.com/Ascend/msdebug/blob/26.1.0/docs/en/user_guide/msdebug_user_guide.md) | Advanced debugging techniques such as memory viewing, core switching, and parsing Core dump files. |
| [msOpProf](https://gitcode.com/Ascend/msopprof/blob/26.1.0/docs/en/user_guide/msopprof_user_guide.md) | Visual performance analysis combined with [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/26.1.0/docs/en/install_guide/mindstudio_insight_install_guide.md), including compute memory heatmaps, cache heatmaps, and code hotspot maps. |

**Step 3: Landing Real Business: From Teaching to Production**  

Deeply study the [Ascend C Programming Guide (Official Tutorial)](https://www.hiascend.com/en/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll) to systematically master core concepts such as multi-level pipelining, data layout, and memory management. On this basis, try to apply the toolchain to the development and tuning of actual business operators, gradually building complete capabilities from prototype verification to production-level delivery.

## 3. FAQ

### 3.1 Compile Error When Compiling the Operator Invocation Program: fatal error: `aclnn_add_custom.h`: No such file or directory

**Problem Symptom**

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

**Root Cause**

During operator deployment, `op_api/include/aclnn_add_custom.h` was not deployed to the correct location, resulting in the header file not being found. One possible reason is that the environment variable `ASCEND_CUSTOM_OPP_PATH` exists in the environment, and its value is either incorrect or contains multiple colon-separated paths. However, when deploying the header file, it is only successfully copied to the first path, and subsequent directories are not deployed.

**Solution**

Delete the environment variable (execute `unset ASCEND_CUSTOM_OPP_PATH`), and then redeploy the operator.

### 3.2 Runtime Error When Executing `execute_add_op`: undefined symbol: `aclnnAddCustomGetWorkspaceSize`

**Problem Symptom**

```text
execute_add_op: symbol lookup error: ./build/execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize
```

**Root Cause**

After deploying the operator, the `.so` file was not added to the environment variable `LD_LIBRARY_PATH` as prompted in the output.

**Solution**

Follow step 3 in [2.3.3 Compiling and Deploying Operators](#233-compiling-and-deploying-operators) to reset the `LD_LIBRARY_PATH` environment variable.

### 3.3 Runtime Error When Setting Breakpoints in msDebug: `WARNING: Unable to resolve breakpoint to any actual locations`

**Problem Symptom**

```text
(msdebug) b add_custom.cpp:23
Breakpoint 1: no locations (pending on future shared library load).
WARNING:  Unable to resolve breakpoint to any actual locations.
```

**Root Cause**

The specified breakpoint line may be an empty line, a comment, or another line where a breakpoint cannot be set, or `/proc/debug_switch` was not set successfully. Refer to the next section for the reason.

**Solution**

Check the source code file to confirm the actual line number of the code, and follow [2.5.1 Enabling Kernel Debug Switch](#251-enabling-kernel-debug-switch) to set `/proc/debug_switch` = 1 on the host machine (note: not inside the container) with root privileges. If the setting cannot be applied successfully, you can only skip this tool experience.

### 3.4 Runtime Error When Executing msDebug `run`: error: `'A' packet returned an error: 8`

**Problem Symptom**

```text
error: 'A' packet returned an error: 8
```

**Root Cause**

The `/proc/debug_switch = 1` setting was not successfully applied. Verify whether the value on the host machine has been changed back to 0. If you are operating in a container environment provided by a cloud service provider, even if `/proc/debug_switch` is successfully set and queried as `1` inside the container,  
this status may be false. For security reasons, the underlying host typically isolates the `/proc` directory through mechanisms such as copy-on-write (CoW), shadow files, or overlay mounts, causing the setting to not actually take effect.

**Solution**

Log in to the host machine (note: not inside the container) with root privileges, and set `/proc/debug_switch = 1` as described in [2.5.1 Enabling Kernel Debug Switch](#251-enabling-kernel-debug-switch). If the setting cannot be applied successfully, you can only skip this tool experience.
