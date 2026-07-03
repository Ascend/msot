# Operator Development Toolchain Quick Start

## 1. Overview

The MindStudio Operator Development Toolchain includes a variety of tools. This document uses the development of a simple addition operator as an example to walk you through the entire operator development process, giving you the firsthand experience of the efficiency and convenience brought by the toolchain.

### 1.1 Preface

#### Experience Map (Only 10 Minutes Required for Core operations)

> **Recommended execution order**: Step 1 is foundational; after completing Step 1, you can try Step 2 or 3; Steps 4, 5, and 6 all depend on the project generated in Step 3, but these three are independent of each other and can be learned on demand.

 | Step | Operation | Core Tool | Operation Duration | Suggested Learning Time |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **Environment Setup** | `CANN Container Image` | 3 min | 5 min |
| **2** | **Operator Design** | `msKPP` | 30 sec | 5 min |
| **3** | **Project Development** | `msOpGen` | 1 min | 20 min |
| **4** | **Anomaly Detection** | `msSanitizer` | 1 min | 10 min |
| **5** | **Native Debugging** | `msDebug` | 1 min | 10 min |
| **6** | **Performance Tuning** | `msOpProf` | 1 min | 10 min |

### 1.2 Environment Setup

👉 **[Important] Strictly follow the [Ascend AI Operator Development Toolchain Learning Environment Setup Guide](installation_guide.md) to complete the environment installation and configuration.**

> [!CAUTION]
> This tutorial is specifically designed for a standardized container environment. Please ensure you complete the container deployment according to the installation guide above. If your current environment does not meet the requirements (such as a bare metal or virtual machine environment), please postpone the experience to avoid issues that are difficult to diagnose due to missing dependencies or configuration differences. Proceed only after the environment meets the requirements.

## 2. Procedure

> [!NOTE]
> The entire subsequent experience session supports quick execution through copy/paste. Follow the steps in each section in order. Do not skip or rearrange the steps.

### 2.1 [Environment] Performing Environment Pre-check

#### 2.1.1 Verifying Environment Variable Configuration

Run the following command to confirm that the system outputs the correct chip SoC model information (for example, 910B4, 910_9392):

```shell
echo $MY_STUDY_VAR_CHIP_SOC_TYPE
```

If the variable is empty, refer to [1.2 Environment Setup](#12-environment-setup) to set it correctly. Ensure this environment variable is properly configured; otherwise, subsequent steps will frequently report errors.

#### 2.1.2 Confirm the Code Repository is Normal

Run the following command. If the directory contents are listed normally, the code repository is correctly in place:

```shell
ls -al ~/ot_demo/msot/example/quick_start
```

If the command reports an error, refer to [1.2 Environment Setup](#12-environment-setup) to complete the preparation.

### 2.2 [Design] Operator Modeling Design (msKPP)

First, design the operator algorithm. With the msKPP tool, you can obtain operator performance modeling results in seconds, estimate performance without hardware, and quickly verify the feasibility of the implementation. Follow the steps to experience the effect first; the principles can be read later:

> [!NOTE] Note  
> **Knowledge Point: Principles of the msKPP Tool**
> msKPP is not a traditional executable program, but a Python class library dedicated to Ascend. You need to import relevant modules, write and execute Python scripts, and generate performance analysis result files to complete the modeling. The internal principle is to pre-collect performance data of various instruction operations in real environments, and then model and estimate various performance overheads based on the operator execution flow defined by the user.

#### 2.2.1 Coding the Python Modeling Script

1. Create a sub-workspace directory

    ```shell
    mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
    ```

2. Develop the Python script

    > [!NOTE]
    > **Knowledge Point (Optional Reading): msKPP's DSL (Domain-Specific Language) Approach**
    > This set of libraries and interfaces is a "dialect" specifically designed for Ascend performance modeling. It requires dedicated learning to master and cannot be written directly using only general Python syntax. However, its usage is relatively simple and can be applied with a little study.
    > Typical development workflow: You need to first import Tensor, Chip, and the instructions required for operator implementation (for example, vadd). Use the `with` statement to enter the context of the operator implementation code, then create Tensors to perform specific operations. The sample script contains detailed comments. For descriptions of other instruction interfaces, refer to the [msKPP Tool Interface Description](https://gitcode.com/Ascend/mskpp/blob/26.0.0/docs/en/api_reference/mskpp_api_reference.md).

    As this is a quick start, copying the prepared msKPP DSL script here is considered development complete (this tutorial focuses on toolchain usage; actual development requires self-implementation):

    ```shell
    \cp -f ~/ot_demo/msot/example/quick_start/mskpp/mskpp_demo.py ./
    ```

#### 2.2.2 Performance Modeling

Run the Python script to start performance modeling. If successful, a `MSKPP{timestamp}` result directory will be automatically generated in the current directory:

```shell
python3 mskpp_demo.py
```

If the script reports an error indicating that the Chip is unsupported, check whether the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` is set correctly. If the variable is empty, refer to [1.2 Environment Setup](#12-environment-setup) to set it correctly.

#### 2.2.3 Viewing Modeling Results

The following is an example of some generated result files:

```text
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

Taking Instruction_statistic.csv as an example, its content is as follows:

| Instruction | Duration (μs) | Cycle | Size (B) | Ops |
| :--------------: | :--------------: | :-------: | :---------: | :------: |
| MOV-GM_TO_UB | 0.3081 | 570 | 6144 | - |
| VADD | 0.0135 | 25 | - | 1536 |
| MOV-UB_TO_GM | 0.4254 | 787 | 3072 | - |

As can be seen from the above content, MOV-UB_TO_GM (moving from UB to GM) has the longest duration and the highest number of instruction cycles, making it a critical path that requires focused attention during performance optimization. In actual development, if such memory transfer operations are found to account for an excessively high proportion of time, priority should be given to optimizing data reuse (tiling) or using more efficient transfer instructions.

### 2.3 [Development] Building the Operator Project (msOpGen)

After the algorithm design is complete, you can proceed to the operator code writing phase. An operator project is relatively complex and contains a large amount of framework code. The msOpGen tool can automatically generate a complete operator project framework, allowing developers to focus on core algorithm implementation and avoid wasting time on repetitive tasks such as project setup and compilation configuration. Follow the steps to experience the effect first; the principle part can be read later:

#### 2.3.1 Generating the Project Framework

1. Create a sub-workspace directory

    Create a subdirectory named `src` as the root directory for the operator source code. All subsequent source code operations will be based on this path:

    ```shell
    mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src/
    ```

2. Develop the operator definition configuration file

    > [!NOTE]
    > **Knowledge Point (Optional Reading): msOpGen input configuration file**
    > A custom-format JSON configuration file, which can be simply analogized to defining a C function declaration, including: the function name, and the type information of input parameters and return values.
    > For example, msopgen_demo.json defines the operator's name, the names, types, and data layout formats of input and output variables.
    > The operator function declaration code is uniformly generated by the tool, i.e., an empty function (with only the function name, input parameters, and return values) is generated, and the function body needs to be implemented by the user.

    Since this is a quick start, copying the prepared configuration file here is considered development complete (this tutorial focuses on toolchain usage; actual development requires self-implementation):

    ```shell
    \cp -f ~/ot_demo/msot/example/quick_start/msopgen/msopgen_demo.json ./
    ```

3. Generate the code framework based on the configuration

    Run the following command to generate the Ascend C operator project. Parameter description: -lan cpp indicates that Ascend C code is to be generated; -c specifies the chip SoC model (processing may differ for different chips):

    ```shell
    msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
    ```

    >[!CAUTION]
    > In the code framework generated by the above command, the implementation of the specific operator is empty and cannot perform addition operations normally. It must be modified according to the content in [Section 2.3.2](#232-implementing-the-core-logic) before it can run properly.

4. View the generated results

    > [!NOTE]Note
    > **Knowledge Point (Optional Reading): Key Concepts**
    > Host side: Code running on the CPU, responsible for data preprocessing, task scheduling, and operator invocation.
    > Kernel side: Code running on the NPU, responsible for executing the actual large-scale parallel computational logic.
    > Tiling: Processing large-scale data in blocks to improve Local Memory utilization and optimize memory access efficiency.

    The following are examples of some generated result files. The generated project structure may appear large and complex, but we **only need to focus on the three C++ files marked as [User Extension Points]**. The rest are framework code and do not need to be viewed or modified unless there are special requirements:

    ```text
    AddCustom
    ├── build.sh                 // Compilation entry script
    ├── CMakeLists.txt           // CMakeLists.txt for the operator project
    ├── framework                // Operator plugin implementation file directory. The generation of single operator model files does not depend on operator adaptation plugins, so no attention is needed.
    │   ├── CMakeLists.txt
    │   └── tf_plugin
    ├── op_host                  // Host side implementation files
    │   ├── add_custom.cpp       // [User extension point] Files for operator prototype registration, shape derivation, information library, tiling implementation, and other content
    │   └── CMakeLists.txt
    ├── op_kernel                // Kernel side implementation files
    │   ├── add_custom.cpp       // [User extension point] operator code implementation file
    │   ├── add_custom_tiling.h  // [User extension point] operator tiling definition file
    │   └── CMakeLists.txt
    └── CMakePresets.json        // Compilation configuration items
    ```

#### 2.3.2 Implementing the Core Logic

> [!NOTE]  
> **Knowledge Point (Optional Reading): Implementation Principles of Operator Core Code Files**  
> op_host/add_custom.cpp: Implements the Tiling computation logic and operator prototype registration on the Host side.  
> op_kernel/add_custom_tiling.h: Defines the data structure for the Tiling block strategy.  
> op_kernel/add_custom.cpp: Implements the specific computational logic of the addition operator on the Kernel side (GM→UB transfer→vector addition→UB→GM write-back).  
> If you need a deeper understanding of the functions and collaboration mechanisms of the three files above, in addition to referring to the code comments, it is recommended to read the *Ascend C Programming Introductory Tutorial (Pure Practical Content)* in detail.  
> The principle of the following `keep_soc_info.py` is explained as follows: This script automatically obtains the SoC information of the current environment and automatically refreshes it into the cpp files.

Implement the specific algorithm logic in the three [User Extension Point] files mentioned above. As this is a quick start, copying the three prepared C++ files here is considered development completion (this tutorial focuses on toolchain usage; in actual development, you need to implement the core logic yourself):

```shell
cd ~/ot_demo/workspace/src/AddCustom/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py get ./op_host/add_custom.cpp
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom.cpp ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom_tiling.h ./op_kernel/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ./op_kernel/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py set ./op_host/add_custom.cpp
```

#### 2.3.3 Operator Compilation and Deployment

1. Compile the operator.

    Run the build script. After success, an operator deployment package in .run format will be generated in the build_out directory (the sed command is used to avoid concurrent pipe issues in certain environments, changing the packaging to serial):

    ```shell
    sed -i 's/--target $target -j$(nproc)/--target $target -j1/g' build.sh
    bash ./build.sh
    ```

2. Deploy the operator.

    >[!NOTE]Note
    > **Knowledge Point: What is Operator Deployment**
    > Operator deployment refers to registering the operator into the CANN framework, which essentially copies the operator's binary files to the system's public directory, enabling other programs to automatically discover and invoke the operator through standard interfaces (such as CANN API or PyTorch). The *.run deployment package format can be simply understood as a self-extracting archive.

    Since the names of operator deployment packages generated on different platforms may vary slightly, run the following script to automatically locate and execute the deployment package (in a fixed environment, this is effectively equivalent to running a command like ./build_out/custom_opp_ubuntu_aarch64.run):

    ```shell
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

3. Add the dynamic library path.

    After successful deployment, append the dynamic library path that the operator depends on as prompted in the terminal:

    ```shell
    export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH
    echo "export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
    ```

#### 2.3.4 Verifying Operator Functionality

> [!CAUTION]
> **NPU device selection**
> Running the following `run.sh` script will actually execute the operator, and it will randomly select an idle card to run the task.
> If you need to specify an NPU card because the randomly selected card has faults or other reasons, use the sequence number (value range: [0, number of NPUs - 1]) returned by the `npu-smi info` command and invoke it as follows: `bash ./run.sh 2`

Run the operator invocation project to verify the operator functionality (this example executes 1.0 + 2.0, with an expected result of 3.0):

```shell
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

If no result is returned within 30 seconds, the NPU card may be busy. You can press Ctrl+C to terminate and switch to another idle card to retry. If an error similar to the following occurs, possible causes include: NPU card abnormality (hardware fault, driver issue, etc.), /dev/hisi_hdc device abnormality (such as unsuccessful mounting in the container, lack of access permissions, device unable to open due to excessive threads, etc.), and insufficient system resources such as memory.
For error code descriptions, see: [ACL Error Codes](https://www.hiascend.com/document/detail/en/canncommercial/850/API/appdevgapi/aclcppdevg_03_1345.html). Please resolve the NPU card fault or switch to another normal card before continuing the experience (for details on specifying an NPU card, see "Notes on NPU device selection" above):

```text
aclrtSetDevice failed. ERROR: xxxxxx
Init acl failed. ERROR: 1
```

#### 2.3.5 Backing up the Kernel-side CMakeLists.txt

The execution of the subsequent three tools requires modifying this CMakeLists.txt. Keep this backup for environment restoration:

```shell
\cp ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak
```

### 2.4 [Detection] Operator Anomaly Detection (msSanitizer)

After completing operator development, you can use the msSanitizer tool to detect serious runtime defects such as memory out-of-bounds, race conditions, uninitialized variables, or synchronization anomalies, thereby efficiently locating potential hidden errors. Follow the steps to experience the effect first; the principle part can be read later:

#### 2.4.1 Modifying Compilation Options

To enable the detection capability, insert the sanitizer compilation option at the first line of the Kernel-side CMakeLists.txt to inject detection stub code:

```shell
cd ~/ot_demo/workspace/src/AddCustom
printf '%s\n' "if(COMMAND add_ops_compile_options)" "  add_ops_compile_options(ALL OPTIONS -sanitizer)" "elseif(COMMAND npu_op_kernel_options)" "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)" "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt;
```

#### 2.4.2 Constructing a Memory Out-of-Bounds Error

Overwrite the original implementation with the prepared source file containing defective code to artificially introduce an out-of-bounds access:

```shell
\cp -f ~/ot_demo/msot/example/quick_start/mssanitizer/bug_code/add_custom.cpp op_kernel/add_custom.cpp
```

>[!NOTE]
>The key modification is as follows (2 * this->tileLength attempts to read twice the length, exceeding the allocation range of xGm in GM memory, triggering an "illegal read"):
>
>```diff
>- AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], this->tileLength);
>+ AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], 2 * this->tileLength);
>```

#### 2.4.3 Recompilation and Deployment

```shell
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

#### 2.4.4 Executing Memory Detection

```shell
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck -- bash run.sh
```

The tool outputs the following error report, indicating successful execution (the example below may vary slightly across versions, which does not affect learning how to use the tool):  

1. illegal read of size 224: indicates an illegal read of 224 bytes.
2. op_kernel/add_custom.cpp:44:9: indicates that the out-of-bounds access occurred at line 44 of add_custom.cpp.

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

>[!NOTE]  
>Even after the operator executes, it can still successfully output the correct result, which demonstrates the value of this tool: memory issues are often sporadic. In most cases, even if a memory anomaly exists, the program can still run normally. Only when the problem accumulates to a critical point will it suddenly crash, making it difficult to locate directly through symptoms.

#### 2.4.5 Restoring Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```shell
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ~/ot_demo/workspace/src/AddCustom/op_kernel/
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.5 [Debugging] Code for Operator Breakpoint Debugging (msDebug)

If the operator functionality is abnormal, you can use the msDebug tool for breakpoint debugging to efficiently locate problems. Follow the steps to experience the effect first; the principle part can be read later:

#### 2.5.1 Enabling Kernel Debugging

>[!CAUTION]
> **msDebug requires root privileges to enable the kernel debugging switch /proc/debug_switch**  
> This switch is disabled by default and can only be modified by the root user. msDebug will only function properly after this switch is enabled.  
> **Operations inside containers are generally ineffective:**  
> Even if you successfully write to `/proc/debug_switch` as root inside a container, the setting **only affects the container view** and does not actually take effect on the kernel, because the host commonly uses mechanisms such as copy-on-write (CoW), shadow files, or overlay mounts to virtualize `/proc`. Therefore, even if `cat /proc/debug_switch` shows `1`, msDebug may still be unusable and return an error during debugging (e.g., `'A' packet returned an error: 8`).  
> **Recommended approach:**  
> If you are in a shared development machine, a regular container, or an environment without host access, contact your system administrator for assistance in enabling it, or switch to a host environment with root privileges to experience this feature.

Check whether the kernel debugging switch debug_switch is enabled:

```shell
cat /proc/debug_switch
```

If the output value is not 1, run the following command on the host machine with root privileges:

```shell
echo 1 > /proc/debug_switch
```

If it cannot be successfully set to 1, the msDebug feature is unavailable, and you can only skip the msDebug experience in this section.

#### 2.5.2 Modifying Compilation Options and Redeploying

1. Modify compilation options.

    Insert the configuration at the first line of the Kernel-side CMakeLists.txt to enable debugging information and disable compilation optimization:

    ```shell
    cd ~/ot_demo/workspace/src/AddCustom
    printf '%s\n' "if(COMMAND add_ops_compile_options)" "  add_ops_compile_options(ALL OPTIONS -g -O0)" "elseif(COMMAND npu_op_kernel_options)" "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)" "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt;
    ```

2. Recompile and deploy the operator.

    ```shell
    bash ./build.sh
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

#### 2.5.3 Setting Debugging Environment Variables

Set `LAUNCH_KERNEL_PATH` through a script to specify the operator obj loading path and import debugging symbol information:

```shell
source ~/ot_demo/msot/example/quick_start/msdebug/set_kernel_obj_env.sh
```

#### 2.5.4 Breakpoint Debugging and Variable Inspection

1. Start the debugger

    ```shell
    cd ~/ot_demo/workspace/src/caller/build
    msdebug execute_add_op
    ```

2. Set breakpoint

    After the (msdebug) prompt appears, set a breakpoint at line 34 of add_custom.cpp:

    ```text
    b add_custom.cpp:34
    ```

    >[!CAUTION]
    >If /proc/debug_switch was not properly enabled on the host machine previously, the breakpoint setting described in the previous section will trigger a warning, and running the `run` command as described in subsequent sections will trigger a debugger error (e.g., 'A' packet returned an error: 8), indicating that msDebug cannot work properly.

3. Run the operator

    Enter run to start the program and wait for the breakpoint to be hit:

    ```text
    run
    ```

    If the following information is displayed, the breakpoint has been hit successfully (the following example may vary slightly between versions, which does not affect learning how to use the tool):

    ```text
    Process 163027 launched: '/root/ot_demo/workspace/src/caller/build/execute_add_op' (aarch64)
    [Launch of Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 on Device 0]
    Process 163027 stopped
    [Switching to focus on Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0, CoreId 1, Type aiv]
    * thread #1, name = 'execute_add_op', stop reason = breakpoint 1.1
        frame #0: 0x00000000000007e0 AddCustom_ab1b6750d7f510985325b603cb06dc8b.o`KernelAdd::Init(this=0x00000000001d78a8, x=0x12c0c0013000, y=0x12c0c001c000, z=0x12c0c0025000, totalLength=16384, tileNum=8) (.vector) at add_custom.cpp:34:9
      31           this->tileLength = this->blockLength / tileNum / BUFFER_NUM;
      32  
      33           // Set the global memory buffer and allocate the global shared memory area that the current AI Core is responsible for
    -> 34           xGm.SetGlobalBuffer((__gm__ DTYPE_X *)x + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
      35           yGm.SetGlobalBuffer((__gm__ DTYPE_Y *)y + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
      36           zGm.SetGlobalBuffer((__gm__ DTYPE_Z *)z + this->blockLength * AscendC::GetBlockIdx(), this->blockLength);
    ```

4. View variable values.

    Run the following command at the breakpoint to display all local variables in the current scope:

    ```text
    var
    ```

5. Exit the debugger.

    ```text
    q
    ```

#### 2.5.5 Restoring Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```shell
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.6 [Tuning] Analyzing Operator Performance (msOpProf)

If the operator performance does not meet expectations, you can use the msOpProf tool to collect runtime performance data for in-depth analysis and optimization, ensuring efficient execution of the operator on different Ascend hardware platforms. Follow the steps to experience the effect first; the principle part can be read later:

#### 2.6.1 Modifying Compilation Options, and Performing Recompilation and Deployment

1. Modify compilation options

    Insert a configuration at the first line of the Kernel-side CMakeLists.txt to enable debugging information:

    ```shell
    cd ~/ot_demo/workspace/src/AddCustom
    printf '%s\n' "if(COMMAND add_ops_compile_options)" "  add_ops_compile_options(ALL OPTIONS -g)" "elseif(COMMAND npu_op_kernel_options)" "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)" "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt;
    ```

    > [!NOTE]
    > **Knowledge Point (Optional Reading): Why the -O optimization level is switched between tools**
    > During debugging, -O0 must be used to disable optimization to support breakpoints and variable inspection, preserving accurate symbol mapping. However, the performance gap between -O0 and -O2 can be several times, so performance analysis must be based on code compiled with -O2 (or the default optimization level); otherwise, the collected data will severely deviate from real-world scenarios and lose reference value.

2. Recompile and deploy the operator

    ```shell
    bash ./build.sh
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

#### 2.6.2 Starting On-Board and Simulation Collection

> [!NOTE] Note
> **Knowledge Point: Differences Between On-Board and Simulation Collection**
> On-board: Accurately captures real hardware characteristics such as operator runtime duration, pipe usage, memory bandwidth, and cache behavior, which are often key metrics that simulators struggle to reproduce with high fidelity.
> Simulation: Provides more complete and stable analysis capabilities in areas such as instruction stream tracing and code hotspot localization, but has limited simulation accuracy for hardware-related behaviors like memory access latency and bandwidth bottlenecks.
> Therefore, it is recommended to combine both methods to leverage their complementary strengths for comprehensive performance diagnosis. If you do not have real hardware (NPU card) in certain scenarios, you can use simulation mode for preliminary performance estimation and hotspot analysis.

1. On-board performance profiling

    ```shell
    cd ~/ot_demo/workspace/src/caller/build
    msopprof --output=./msopprof_output_npu ./execute_add_op
    ```

2. Simulator performance profiling

    ```shell
    msopprof simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msopprof_output_sim ./execute_add_op
    ```

#### 2.6.3 Viewing Performance Data Results

The tool generates result files in .csv and .bin formats in the specified `--output` directory. If no errors are reported in the output, it indicates successful execution:

- csv file

For example, `MemoryUB.csv`. Opening it reveals the following information:  
The data shows that the task is evenly divided into 8 blocks, all scheduled to run on the Vector Core. For instance, the bandwidth of Block 0 (1.02 GB/s) is significantly higher than that of Block 1 (0.77 GB/s). If the difference is too large, it may indicate room for optimization:

  | block_id | sub_block_id | aiv_time (μs) | aiv_total_cycles | aiv_ub_read_bw_vector (GB/s) | aiv_ub_write_bw_vector (GB/s) |
  |:--------:|:------------:|:------------: | :----------------: | : ---------------------------:|:----------------------------:|
  |    0     |   vector0    |  7.456666  |      13422      |          1.023164           |           0.511582           |
  |    1     |   vector0    |  9.914444  |      17846      |          0.769523           |           0.384762           |
  |    2     |   vector0    |  10.001111 |      18002      |          0.762855           |           0.381427           |
  |    3     |   vector0    |  9.684444  |      17432      |          0.787799           |           0.393899           |
  |    4     |   vector0    |  9.747222  |      17545      |          0.782725           |           0.391363           |
  |    5     |   vector0    |  9.062222  |      16312      |          0.84189            |           0.420945           |
  |    6     |   vector0    |  9.293889  |      16729      |          0.820904           |           0.410452           |
  |    7     |   vector0    |  8.658889  |      15586      |          0.881105           |           0.440553           |

- bin file

You can open it using the `MindStudio Insight` tool to visually display various performance views, such as: compute-memory heatmaps, cache heatmaps, and operator code hotspot maps.

  > [!NOTE]
  > If you want to experience visual chart viewing, please refer to [MindStudio Insight Documentation](https://gitcode.com/Ascend/msinsight/blob/26.0.0/docs/zh/user_guide/mindstudio_insight_install_guide.md) to install the Insight tool.

#### 2.6.4 Reverting Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```shell
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.7 [Completion] Advanced Learning Path

Congratulations on completing the introductory experience of the Operator Development Toolchain.

At this point, you have fully walked through the complete operator development process of "Design → Development → Detection → Debugging → Tuning" and have practically experienced the basic usage of the following five core tools:

| Tool | Core Capability You Have Mastered |
| ----------- | --------------------------------- |
| **msKPP** | Write DSL scripts for operator performance modeling and estimate performance bottlenecks without hardware conditions. |
| **msOpGen** | Automatically generate operator project frameworks based on configuration files, and complete compilation, deployment, and functional verification. |
| **msSanitizer** | Inject detection stub code to locate the source code positions of runtime defects such as memory out-of-bounds. |
| **msDebug** | Start breakpoint debugging, set breakpoints in NPU operator code, and inspect variables. |
| **msOpProf** | Collect performance data through both on-device and simulation modes, and analyze the execution efficiency of each block. |

If you want to continue with advanced experience, refer to the following steps:

**Step 1: Consolidate the foundation: Independently develop a new operator**  

Refer to the AddCustom in this tutorial and try to independently implement a subtraction operator (SubCustom) or multiplication operator (MulCustom), focusing on: differences in Tiling strategy design, the use of different computation instructions (such as `vsub`, `vmul`), and the end-to-end compilation and deployment process.

**Step 2: Dive into the tools: Master the advanced features of each tool**  

This tutorial only covers the introductory usage of each tool. Each tool provides richer advanced capabilities. It is recommended to visit the corresponding repository's *User Guide* for in-depth learning as needed:

| Tool | Advanced Capabilities |
| ------ | -------------- |
| [msKPP](https://gitcode.com/Ascend/mskpp/blob/26.0.0/docs/en/user_guide/mskpp_user_guide.md) | Modeling using cache hit rate, on-the-fly conversion, and performance comparison analysis of multiple Tiling solutions. |
| [msOpGen](https://gitcode.com/Ascend/msopgen/blob/26.0.0/docs/en/user_guide/msopgen_user_guide.md) | Customization of complex operator templates, project generation for multi-input multi-output operators, etc. |
| [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/26.0.0/docs/en/user_guide/mssanitizer_user_guide.md) | Race condition detection, synchronization anomaly diagnosis, uninitialized variable checking, and more detection modes. |
| [msDebug](https://gitcode.com/Ascend/msdebug/blob/26.0.0/docs/en/user_guide/msdebug_user_guide.md) | Advanced debugging techniques such as memory viewing, core switching, and parsing Core dump files. |
| [msOpProf](https://gitcode.com/Ascend/msopprof/blob/26.0.0/docs/en/user_guide/msopprof_user_guide.md) | Visual performance analysis combined with [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/26.0.0/docs/en/user_guide/mindstudio_insight_install_guide.md), including compute-memory heatmaps, cache heatmaps, and code hotspot maps. |

**Step 3: Implement in practice: From learning to production**  

Deeply study the [Ascend C Programming Guide (Official Tutorial)](https://www.hiascend.com/zh/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll), systematically master core concepts such as multi-level pipelining, data layout, and memory management. On this basis, try to apply the toolchain to the development and tuning of actual business operators, gradually building complete capabilities from prototype verification to production-grade delivery.

## 3. FAQs

### 3.1 Error when running mskpp_demo.py: Exception: Parameter chip_name in Chip is unsupported

- Symptom

```text
root@localhost:~/ot_demo/workspace/mskpp# python3 mskpp_demo.py
Traceback (most recent call last):
  File "/root/ot_demo/workspace/mskpp/mskpp_demo.py", line 28, in <module>
    with Chip("Ascend" + chip_name) as chip:  # The format is Ascendxxxyy, where xxxyy is the specific chip SoC model actually used by the user, which can be queried via npu-smi info
         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mskpp/core/chip.py", line 30, in __init__
    self.param_transfer()
  File "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mskpp/core/chip.py", line 110, in param_transfer
    raise Exception("Parameter chip_name in Chip is unsupported")
Exception: Parameter chip_name in Chip is unsupported
```

- Cause

The `MY_STUDY_VAR_CHIP_SOC_TYPE` environment variable is missing.

- Solution

Refer to Section 1.3 of the [Operator Development Toolchain Learning Environment Installation Guide](https://gitcode.com/Ascend/msot/blob/26.0.0/docs/en/quick_start/installation_guide.md) to reconfigure it.

### 3.2 Error When Compiling the Operator Invocation Program: fatal error: aclnn_add_custom.h: No such file or directory

- Symptom

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

- Cause

During operator deployment, `op_api/include/aclnn_add_custom.h` was not deployed to the correct location, resulting in the header file not being found. One possible reason is that the environment variable `ASCEND_CUSTOM_OPP_PATH` exists in the environment, and its value is either incorrect or contains multiple colon-separated paths. However, during header file deployment, the file is only successfully copied to the first path, and subsequent directories are not deployed.

- Solution

Delete the environment variable (run `unset ASCEND_CUSTOM_OPP_PATH`), then redeploy the operator.

### 3.3 Exception Error When Executing execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize

- Symptom

```text
execute_add_op: symbol lookup error: ./build/execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize
```

- Cause

After deploying the operator, the so file was not added to the environment variable LD_LIBRARY_PATH as prompted by the output.

- Solution

Follow step 3 in [2.3.3 Operator Compilation and Deployment](#233-operator-compilation-and-deployment) to reset the LD_LIBRARY_PATH environment variable.

### 3.4 Error When Setting Breakpoint in msDebug: WARNING: Unable to resolve breakpoint to any actual locations

- Symptom

```text
(msdebug) b add_custom.cpp:23
Breakpoint 1: no locations (pending on future shared library load).
WARNING:  Unable to resolve breakpoint to any actual locations.
```

- Cause

The specified breakpoint line may be an empty line, a comment, or another line where a breakpoint cannot be set, or `/proc/debug_switch` was not set successfully. Refer to the next section for the cause.

- Solution

Check the source code file to confirm the actual line number of the code; follow [2.5.1 Enabling Kernel Debugging](#251-enabling-kernel-debugging) to set `/proc/debug_switch` = 1 with root privileges on the host machine (note: not inside the container).

### 3.5 Error at Runtime When Executing msDebug run: error: 'A' packet returned an error: 8

- Symptom

```text
error: 'A' packet returned an error: 8
```

- Cause

The `/proc/debug_switch = 1` was not set successfully. Check whether it has been reset to 0 on the host machine, or if you are operating in a container environment provided by a cloud service provider, even if `/proc/debug_switch` is successfully set and queried as 1 inside the container, this state may be false. For security reasons, the underlying host typically isolates the /proc directory through mechanisms such as copy-on-write (CoW), shadow files, or overlay mounts, causing the setting to not actually take effect.

- Solution

Log in to the host machine with root privileges (note: not inside the container), and set `/proc/debug_switch` = 1 as described in [2.5.1 Enabling Kernel Debugging](#251-enabling-kernel-debugging). If the setting cannot be applied successfully, you can only skip this tool experience.
