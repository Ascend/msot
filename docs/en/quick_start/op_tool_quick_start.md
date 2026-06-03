# Operator Development Toolchain Quick Start

<br>

## 1. Overview

The MindStudio operator development toolchain includes a variety of tools. This document uses the development of a simple addition operator as an example to guide you through the entire operator development process, allowing you to intuitively experience the efficiency and convenience brought by the toolchain.

### 1.1 About This Document

**Experience Map (Core operations take only 10 minutes)**     
> **Recommended Procedure**: Step 1 is the foundation; after completing Step 1, you can experience Step 2 or Step 3; Steps 4, 5, and 6 all depend on the project generated in Step 3, but these three are independent of each other and can be learned as needed.

 | Step | Phase | Core Tools | Measured Operation Time | Recommended Theory Learning |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **Environment Preparation** | `CANN` | Container ≤ 5 minutes, Bare metal ≥ 20 minutes | 5 minutes |
| **2** | **Operator Design** | `msKPP` | 30 seconds | 5 minutes |
| **3** | **Project Development** | `msOpGen` | 1 minute | 20 minutes |
| **4** | **Anomaly Detection** | `msSanitizer` | 1 minute | 10 minutes |
| **5** | **Native Debugging** | `msDebug` | 1 minute | 10 minutes |
| **6** | **Performance Tuning** | `msOpProf` | 1 minute | 10 minutes |

### 1.2 Environment Preparation

Please strictly follow the *[Ascend AI Operator Development Toolchain Learning Environment Installation Guide](installation_guide.md)* to complete the environment and workspace configuration.

>💡 <span style="color:#a10000;">**Important Note**</span>: The subsequent experience phases fully support Copy/Paste command execution. To avoid exceptions, even if you have a similar environment, please verify dependencies and environment variables according to the guide above. If you encounter exceptions, refer to [3. FAQ](#3-faq).

## 2. Procedure

### 2.1 [Environment] Runtime Environment Pre-check

#### 2.1.1 Verifying Environment Variable Configuration

Run the following command to confirm that the system outputs the correct chip SoC model (e.g., 910B4, 910_9392):

```shell
echo $MY_STUDY_VAR_CHIP_SOC_TYPE
```

If this variable is empty, refer to [1.2 Environment Preparation](#12-environment-preparation) for correct configuration.

> [!CAUTION] Note    
> Ensure that the MY_STUDY_VAR_CHIP_SOC_TYPE environment variable is correctly configured; otherwise, subsequent steps will frequently encounter runtime errors. This variable is intended for learning environments only and **must not be used in official commercial versions**.

#### 2.1.2 Confirming Python Packages Are Installed

Run the following command. If "All is OK" is output, it indicates that the required Python packages and their versions meet the specifications:

```shell
python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"
```

If a runtime error occurs, refer to [1.2 Environment Preparation](#12-environment-preparation) for proper installation.

#### 2.1.3 Confirming the Code Repository Is Normal

Run the following command. If the directory contents are listed normally, the code repository is correctly in place:

```shell
ls -al ~/ot_demo/msot/example/quick_start
```

If a runtime error occurs, refer to [1.2 Environment Preparation](#12-environment-preparation) to complete the correct preparation.

### 2.2 [Design] Operator Modeling Design (msKPP)

First, design the operator algorithm. With the msKPP tool, you can obtain operator performance modeling results in seconds, estimate performance without hardware, and quickly verify the feasibility of the implementation plan. Follow the steps to experience the effect first; the principles can be read later:

> [!NOTE] Note   
> **msKPP Tool Principles**   
> msKPP is not a traditional executable program but a dedicated Python class library for Ascend. Users need to import relevant modules, write and execute Python scripts to generate performance analysis result files for modeling. The internal principle involves pre-collecting performance data of various instruction operations in real environments and modeling and estimating various performance overheads based on the user-defined operator execution flow.

#### 2.2.1 Writing a Python Modeling Script

1. Create a sub-workspace directory

    ```shell
    mkdir -p ~/ot_demo/workspace/mskpp && cd ~/ot_demo/workspace/mskpp
    ```

2. Develop the Python script

    > [!NOTE]Note  
    > **msKPP's DSL (Domain-Specific Language) Solution**   
    > This set of libraries and interfaces is a "dialect" specifically designed for Ascend performance modeling. It requires dedicated learning to master and cannot be written directly using only general Python syntax. However, its usage is relatively simple and can be applied after a brief study.
    > Standard development process: You must first import Tensor, Chip, and the instructions necessary for operator implementation (e.g., vadd). Use the `with` statement to enter the context of the operator implementation code, and then create Tensors to perform specific operations. The sample script contains detailed comments. For descriptions of other instruction interfaces, refer to the *[msKPP Tool Interface Description](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/api_reference/mskpp_api_reference.md)*.

    As this is a quick start, copying the prepared msKPP DSL script here is considered development completion (this tutorial focuses on toolchain usage; actual development requires self-implementation):

    ```shell
    \cp -f ~/ot_demo/msot/example/quick_start/mskpp/mskpp_demo.py ./
    ```

#### 2.2.2 Executing Performance Modeling

Execute the Python script to start performance modeling. If successful, a result directory named "MSKPP{timestamp}" will be automatically generated in the current directory:

```shell
python3 mskpp_demo.py
```

If the script reports a Runtime Error indicating that the Chip is unsupported, verify that the environment variable `MY_STUDY_VAR_CHIP_SOC_TYPE` is set correctly. If the variable is empty, refer to [1.2 Environment Preparation](#12-environment-preparation) to set it correctly.

#### 2.2.3 Viewing Modeling Results

The following result directory is generated:

```text
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

Taking Instruction_statistic.csv as an example, its content is as follows:

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

    ```shell
    mkdir -p ~/ot_demo/workspace/src && cd ~/ot_demo/workspace/src/
    ```

2. Develop the operator definition configuration file.

    >[!NOTE]Note   
    >**Key Point (Optional Reading): msOpGen Input Configuration File**   
    >A custom-format JSON configuration file, which can be simply analogized to defining a C function declaration, including the function name, input parameters, and return value type information.
    >For example, `msopgen_demo.json` defines the operator's name, the names, types, and data layout formats of its input and output variables.
    >The operator function declaration code is uniformly generated by the tool, which produces an empty function (with only the function name, input parameters, and return value). The function body needs to be implemented by the user.

    As this is a quick start guide, copying the prepared configuration file here is considered development complete (this tutorial focuses on toolchain usage; actual development requires self-implementation):

    ```shell
    \cp -f ~/ot_demo/msot/example/quick_start/msopgen/msopgen_demo.json ./
    ```

3. Generate code framework based on configuration.

    Execute the following command to generate an Ascend C operator project. Parameter description: -lan cpp indicates generating Ascend C code; -c specifies the chip SoC model (processing may differ across different chips):

    ```shell
    msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
    ```

4. View generated results.

    >[!NOTE]Note   
    >**Key Point (Optional Reading): Key Concepts**       
    > Host Side: Code running on the CPU, responsible for data preprocessing, task scheduling, and operator invocation.   
    > Kernel Side: Code running on the NPU, responsible for executing the actual large-scale parallel computation logic.   
    > Tiling: Partitioning large-scale data into blocks to improve Local Memory utilization and optimize memory access efficiency.

The generated project structure may appear large and complex, but we **only need to focus on the three C++ files marked as [User Extension Points]**. The rest are framework code, which do not need to be viewed or modified unless there are special requirements:

    ```text
    AddCustom
    ├── build.sh                 // Build Entry Script
    ├── cmake                    // Build Project Script
    ├── CMakeLists.txt           // CMakeLists.txt of the Operator Project
    ├── scripts                  // Directory for Custom Operator Project Packaging Scripts
    ├── framework                // Operator plugin implementation file directory. The generation of a single-operator model file does not depend on the operator adaptation plugin, so no attention is required.
    │   ├── CMakeLists.txt
    │   └── tf_plugin
    ├── op_host                  // Host-side implementation file
    │   ├── add_custom.cpp       // [User Extension Point] Files for operator prototype registration, shape inference, information library, and tiling implementation.
    │   ├── add_custom_tiling.h  // [User Extension Point] Operator tiling definition file
    │   └── CMakeLists.txt
    ├── op_kernel                // Kernel-side implementation file
    │   ├── add_custom.cpp       // [User Extension Point] Operator Code Implementation File
    │   └── CMakeLists.txt
    └── CMakePresets.json        // Compilation Configuration Item
    ```

#### 2.3.2 Implementing Core Logic

> [!NOTE] Note
> **Key Point (Optional Reading): Implementation Principles of Operator Kernel Code Files**
> op_host/add_custom_tiling.h: Defines the data structure for the Tiling strategy.
> op_host/add_custom.cpp: Implements the Tiling computation logic on the Host side and operator prototype registration.
> op_kernel/add_custom.cpp: Implements the specific computation logic of the addition operator on the Kernel side (GM→UB transfer→vector addition→UB→GM write-back).
> If you need a deeper understanding of the functions and collaboration mechanisms of the three files above, in addition to referring to the code comments, it is recommended that you read [Ascend C Programming Introductory Tutorial (Pure Practical Information)](https://www.hiascend.com/developer/blog/details/0239124507827469022) in detail.
> The following `keep_soc_info.py` is used to process SoC information. Since this information varies by environment, it cannot be mechanically overwritten and must use the actual configuration in the current system.

Implement the specific algorithm logic in the three [User Extension Point] files mentioned above. As this is a quick start, copying the three prepared C++ files here is considered development completion (this tutorial focuses on toolchain usage; actual development requires implementing the core logic yourself):

```shell
cd ~/ot_demo/workspace/src/AddCustom/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py get ./op_host/add_custom.cpp
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom_tiling.h ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_host/add_custom.cpp ./op_host/
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ./op_kernel/
python3 ~/ot_demo/msot/example/quick_start/msopgen/keep_soc_info.py set ./op_host/add_custom.cpp
```

#### 2.3.3 Compiling and Deploying Operators

1. Compile the operator.

    Execute the build script. Upon success, an operator deployment package in .run format will be generated in the build_out directory (the sed command is used to avoid concurrent pipe issues in certain environments, making the packaging process serial):

    ```shell
    sed -i 's/--target $target -j$(nproc)/--target $target -j1/g' build.sh
    bash ./build.sh
    ```

2. Deploy the operator.

    >[!NOTE] Note   
    >**Key Point: What is Deploying Operators**  
    > Deploying operators refers to registering the operator with the CANN framework. Essentially, it involves copying the operator's binary files to a system public directory, allowing other programs to automatically discover and invoke the operator through standard interfaces (such as CANN API or PyTorch). The *.run deployment package format can be simply understood as a self-extracting archive.

    Since the names of operator deployment packages generated on different platforms vary slightly, execute the following script to automatically locate and run the deployment package (in a fixed environment, this is effectively equivalent to executing a command like `./build_out/custom_opp_ubuntu_aarch64.run`):

    ```shell
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

3. Add the dynamic library path.

    After successful deployment, append the dynamic library path that the operator depends on as prompted by the terminal:

    ```shell
    export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH
    echo "export LD_LIBRARY_PATH=${ASCEND_OPP_PATH}/vendors/customize/op_api/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
    ```

#### 2.3.4 Verifying Operator Functionality

>[!CAUTION]Note   
>**Notes on NPU Device Selection**   
>Executing the following `run.sh` script will actually run the operator. For ease of learning, it is assumed that all NPU cards in the environment are of the same model, and the system will randomly select an idle card to execute the task.
>If you need to specify an NPU card due to reasons such as a fault on the randomly selected card, use the NPU information returned by the `npu-smi info` command and call it with its sequence number (value range: [0, number of NPUs - 1]) as follows:
>
> ```shell
> bash ./run.sh 2
> ```

Execute the operator invocation project to verify the operator functionality (this example executes 1.0 + 2.0, with an expected result of 3.0):

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

If no result is returned for more than 30 seconds, the NPU card may be busy. You can press Ctrl+C to terminate and switch to another idle card to retry. If an error similar to the following occurs, possible causes include: NPU card abnormality (hardware fault, driver issue, etc.), /dev/hisi_hdc device abnormality (such as unsuccessful mounting in the container, lack of access permissions, device unable to open due to excessive threads, etc.), and insufficient system resources such as memory.    
For error code descriptions, see: [ACL Error Code Table](https://www.hiascend.com/document/detail/en/canncommercial/850/API/appdevgapi/aclcppdevg_03_1345.html). Please resolve the NPU card fault or switch to another normal card before continuing the experience (see "Notes on NPU Device Selection" above for the method to specify an NPU card):

```text
aclrtSetDevice failed. ERROR: xxxxxx
Init acl failed. ERROR: 1
```

#### 2.3.5 Backing Up the Kernel-Side CMakeLists.txt

The execution of the subsequent three tools requires modification of this CMakeLists.txt. Keep this backup for restoring the environment:

```shell
\cp ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak
```

### 2.4 [Detection] Operator Anomaly Detection (msSanitizer)

After the operator development is complete, you can use the msSanitizer tool to detect serious runtime defects such as memory out-of-bounds, race conditions, uninitialized variables, or synchronization anomalies, thereby efficiently locating potential hidden errors. Follow the operation to experience the effect first; the principle part can be read later:

#### 2.4.1 Modifying Compilation Options

To enable the detection capability, you need to insert the sanitizer compilation option at the first line of the CMakeLists.txt on the Kernel side to inject detection stub code:

```shell
cd ~/ot_demo/workspace/src/AddCustom
printf '%s\n' "if(COMMAND add_ops_compile_options)" "  add_ops_compile_options(ALL OPTIONS -sanitizer)" "elseif(COMMAND npu_op_kernel_options)" "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)" "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt;
```

#### 2.4.2 Constructing a Memory Out-of-Bounds Error

Overwrite the original implementation with the prepared source file containing defective code to artificially introduce an out-of-bounds access:

```shell
\cp -f ~/ot_demo/msot/example/quick_start/mssanitizer/bug_code/add_custom.cpp op_kernel/add_custom.cpp
```

The key modification is as follows (2 * this->tileLength attempts to read twice the length, exceeding the allocation range of xGm in GM memory, triggering an "illegal read"):

```diff
- AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], this->tileLength);
+ AscendC::DataCopy(xLocal, xGm[progress * this->tileLength], 2 * this->tileLength);
```

#### 2.4.3 Recompiling and Deploying

```shell
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

#### 2.4.4 Executing Memory Sanitization

```shell
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck -- bash run.sh
```

If the tool outputs the following error report, it indicates successful execution:

1. illegal read of size 224: Indicates an illegal read of 224 bytes.
2. op_kernel/add_custom.cpp:44:9: Indicates that the out-of-bounds access occurred at line 44 of add_custom.cpp.

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

#### 2.4.5 Reverting Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```shell
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp ~/ot_demo/workspace/src/AddCustom/op_kernel/
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.5 [Debugging] Breakpoint Debugging of Operator Code (msDebug)

If the operator functions abnormally, you can use the msDebug tool for breakpoint debugging to efficiently locate issues. Follow the steps to experience the effect first; the principles can be read later:

#### 2.5.1 Enabling Kernel Debug Switch

>[!CAUTION] Note   
>**msDebug requires root privileges**       
> msDebug requires the kernel debug switch /proc/debug_switch to be enabled to function properly, but it is disabled by default for security reasons and requires root privileges to enable.   
> This may not be feasible in many environments (such as shared development machines or containers). In such cases, please contact your system administrator to enable it, or experience this section in a privileged container.

Check whether the kernel debug switch `debug_switch` is enabled:

```shell
cat /proc/debug_switch
```

If the output value is not 1, execute the following command with root privileges **(It is best to execute it on the host machine if possible; in some scenarios, setting it inside a container may not actually take effect)**:

```shell
echo 1 > /proc/debug_switch
```

If it cannot be successfully set to 1, the msDebug function is unavailable, and you can only skip the msDebug experience in this section.

#### 2.5.2 Modifying Compilation Options and Redeploying

1. Modify compilation options.

    Insert the configuration at the first line of the Kernel-side CMakeLists.txt to enable debug information and disable compilation optimization:

    ```shell
    cd ~/ot_demo/workspace/src/AddCustom
    printf '%s\n' "if(COMMAND add_ops_compile_options)" "  add_ops_compile_options(ALL OPTIONS -g -O0)" "elseif(COMMAND npu_op_kernel_options)" "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)" "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt;
    ```

2. Recompile and deploy the operator.

    ```shell
    bash ./build.sh
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

#### 2.5.3 Setting Debug Environment Variables

Set LAUNCH_KERNEL_PATH via a script to specify the operator obj loading path and import debug symbol information:

```shell
source ~/ot_demo/msot/example/quick_start/msdebug/set_kernel_obj_env.sh
```

#### 2.5.4 Breakpoint Debugging and Variable Inspection

1. Start the debugger

    ```shell
    cd ~/ot_demo/workspace/src/caller/build
    msdebug execute_add_op
    ```

2. Set breakpoint.

    After the (msdebug) prompt appears, set a breakpoint at line 34 of add_custom.cpp:

    ```text
    b add_custom.cpp:34
    ```

    >[!CAUTION] Note   
    >**If operating in a managed container environment directly provisioned on the cloud platform, pay special attention that `/proc/debug_switch = 1` may be a false state.**       
    > Even if `/proc/debug_switch` is successfully set and queried as `1` within the container, this value may not have actually taken effect. For security isolation reasons, the underlying host typically virtualizes or intercepts the `/proc` directory through mechanisms such as Copy-on-Write (CoW), shadow files, or overlay mounts, causing write operations to only affect the container view without reflecting the actual kernel state.    
    > In this case, executing the breakpoint setting described in the previous section will trigger a warning; and when running the `run` command as described in subsequent sections, the following error will be reported:
    > 
    > ```text
    > error: 'A' packet returned an error: 8
    > ```
    > 
    > Please log in to the **host machine**, execute `echo 1 > /proc/debug_switch` with root privileges, and then execute `cat /proc/debug_switch` to confirm it is successfully set to 1.    
    > If you cannot log in to the host machine, or cannot successfully set it on the host, or do not have the conditions to switch to another suitable environment, you can only skip the hands-on experience of msDebug in this section.

3. Run the operator.

    Enter run to start the program and wait for the breakpoint to be hit:

    ```shell
    run
    ```

    If the following information is displayed, the breakpoint has been hit successfully:

    ```text
    Process 163027 launched: '/root/ot_demo/workspace/src/caller/build/execute_add_op' (aarch64)
    [Launch of Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 on Device 0]
    Process 163027 stopped
    [Switching to focus on Kernel AddCustom_ab1b6750d7f510985325b603cb06dc8b_0, CoreId 1, Type aiv]
    * thread #1, name = 'execute_add_op', stop reason = breakpoint 1.1
        frame #0: 0x00000000000007e0 AddCustom_ab1b6750d7f510985325b603cb06dc8b.o`KernelAdd::Init(this=0x00000000001d78a8, x=0x12c0c0013000, y=0x12c0c001c000, z=0x12c0c0025000, totalLength=16384, tileNum=8) (.vector) at add_custom.cpp:34:9
      31           this->tileLength = this->blockLength / tileNum / BUFFER_NUM;
      32  
      33           // Set up the global memory buffer and allocate the global shared memory area for which the current AI Core is responsible.
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

```shell
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.6 [Tuning] Analyzing Operator Performance (msOpProf)

If the operator performance does not meet expectations, you can use the msOpProf tool to collect runtime performance data for in-depth analysis and optimization, ensuring efficient execution of the operator on different Ascend hardware platforms. Follow the steps to experience the effect first; the principles can be read later:

#### 2.6.1 Modifying Compilation Options and Recompiling/Deploying

1. Modify compilation options.

    Insert a configuration line at the first line of the Kernel-side CMakeLists.txt to enable debug information:

    ```shell
    cd ~/ot_demo/workspace/src/AddCustom
    printf '%s\n' "if(COMMAND add_ops_compile_options)" "  add_ops_compile_options(ALL OPTIONS -g)" "elseif(COMMAND npu_op_kernel_options)" "  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)" "endif()" | cat - op_kernel/CMakeLists.txt > tmp && mv -f tmp op_kernel/CMakeLists.txt;
    ```

    >[!NOTE]Note
    >**Key Point (Optional Reading): Why the -O optimization level is switched back and forth between tools**
    >During the debugging phase, to support breakpoints and variable inspection, -O0 must be used to disable optimization and preserve accurate symbol mapping. However, the performance gap between -O0 and -O2 can be several times, so performance analysis must be based on code compiled with -O2 (or the default optimization level). Otherwise, the collected data will severely deviate from real-world scenarios and lose its reference value.

2. Recompile and deploy the operator.

    ```shell
    bash ./build.sh
    MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
    ```

#### 2.6.2 Starting On-Board and Simulation Collection

>[!NOTE]Note
>**Differences between on-board and simulation collection information**
> On-board: Can accurately capture operator runtime, Pipe usage, memory bandwidth, cache behavior, and other real hardware characteristics, which are often key metrics that simulators struggle to reproduce with high fidelity.
> Simulation: Provides more complete and stable analysis capabilities in areas such as instruction stream tracing and code hotspot localization, but has limited simulation accuracy for hardware-related behaviors like memory access latency and bandwidth bottlenecks.
> Therefore, it is recommended to combine both methods to complement each other's strengths for comprehensive performance diagnosis. If you do not have real hardware (NPU cards) in certain scenarios, you can use simulation mode for preliminary performance estimation and hotspot analysis.

1. Perform on-board performance profiling.

    ```shell
    cd ~/ot_demo/workspace/src/caller/build
    msprof op --output=./msprof_output_npu ./execute_add_op
    ```

2. Perform simulator performance profiling.

    ```shell
    msprof op simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msprof_output_sim ./execute_add_op
    ```

#### 2.6.3 Viewing Performance Data Results

The tool generates result files in .csv and .bin formats in the specified --output directory. If no errors are reported in the output, the execution is successful:

- CSV files

For example, opening MemoryUB.csv reveals the following information:
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

  >[!NOTE]
  >To experience visual chart viewing, please refer to the <a href="https://gitcode.com/Ascend/msinsight/blob/master/docs/en/user_guide/mindstudio_insight_install_guide.md" target="_blank">MindStudio Insight Tool Documentation</a> to install the Insight tool.

#### 2.6.4 Reverting Manual Modifications

To prepare for subsequent tool usage, revert the manual modifications:

```shell
\cp -f ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt.bak ~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt
```

### 2.7 [Completion] Advanced Learning Path

Congratulations on completing the introductory experience of the Operator Development Toolchain.

At this point, you have fully walked through the entire operator development process of "Design → Develop → Detect → Debug → Tune" and have practically experienced the basic usage of the following five core tools:

| Tool | Core Capabilities You Have Mastered |
| ----------- | --------------------------------- |
| **msKPP** | Write DSL scripts for operator performance modeling and estimate performance bottlenecks without hardware |
| **msOpGen** | Automatically generate operator project frameworks based on configuration files, and complete compilation, deployment, and functional verification |
| **msSanitizer** | Inject detection stub code to locate the source code location of runtime defects such as memory out-of-bounds |
| **msDebug** | Start breakpoint debugging, set breakpoints in NPU operator code, and inspect variables |
| **msOpProf** | Collect performance data through both on-board and simulation modes, and analyze the execution efficiency of each Block |

If you want to continue with advanced experience, you can refer to the following steps:

**Step 1: Consolidate the Foundation: Independently Develop a New Operator**  

Refer to the AddCustom example in this tutorial and try to independently implement a subtraction operator (SubCustom) or multiplication operator (MulCustom), focusing on: differences in Tiling strategy design, the use of different computation instructions (such as `vsub`, `vmul`), and the end-to-end compilation and deployment process.

**Step 2: Dive into Tools: Master the Advanced Features of Each Tool**  

This tutorial only covers the introductory usage of each tool. Each tool offers richer advanced capabilities. It is recommended to access the corresponding repository's *User Guide* for in-depth learning as needed:

| Tool | Advanced Capability Description |
|------|---------------------------------|
| [msKPP](https://gitcode.com/Ascend/mskpp/blob/master/docs/en/user_guide/mskpp_user_guide.md) | Modeling using cache hit rate, in-line conversion, and performance comparison analysis of multiple Tiling strategies. |
| [msOpGen](https://gitcode.com/Ascend/msopgen/blob/master/docs/en/user_guide/msopgen_user_guide.md) | Complex operator template customization, project generation for multi-input multi-output operators, etc. |
| [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/master/docs/en/user_guide/mssanitizer_user_guide.md) | Race condition detection, synchronization anomaly diagnosis, uninitialized variable checking, and more detection modes. |
| [msDebug](https://gitcode.com/Ascend/msdebug/blob/master/docs/en/user_guide/msdebug_user_guide.md) | Advanced debugging techniques such as memory viewing, core switching, and parsing Core dump files. |
| [msOpProf](https://gitcode.com/Ascend/msopprof/blob/master/docs/en/user_guide/msopprof_user_guide.md) | Visual performance analysis combined with [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/master/docs/en/user_guide/mindstudio_insight_install_guide.md), including compute memory heatmaps, cache heatmaps, and code hotspot maps. |

**Step 3: Landing Real Business: From Teaching to Production**  

Deeply study the [*Ascend C Programming Guide (Official Tutorial)*](https://www.hiascend.com/en/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll) to systematically master core concepts such as multi-level pipelining, data layout, and memory management. On this basis, try to apply the toolchain to the development and tuning of actual business operators, gradually building complete capabilities from prototype verification to production-level delivery.

## 3. FAQ

### Error When Executing mskpp_demo.py: Exception: Parameter chip_name in Chip Is Unsupported

**Problem Symptom**

```text
root@localhost:~/ot_demo/workspace/mskpp# python3 mskpp_demo.py
Traceback (most recent call last):
  File "/root/ot_demo/workspace/mskpp/mskpp_demo.py", line 28, in <module>
    with Chip("Ascend" + chip_name) as chip:  # Ascendxxxyy, xxxyy indicates the actual SoC model, which can be queried through the npu-smi info command.
         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mskpp/core/chip.py", line 30, in __init__
    self.param_transfer()
  File "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages/mskpp/core/chip.py", line 110, in param_transfer
    raise Exception("Parameter chip_name in Chip is unsupported")
Exception: Parameter chip_name in Chip is unsupported
```

**Root Cause**

The `MY_STUDY_VAR_CHIP_SOC_TYPE` environment variable is missing.

**Solution**

Refer to Section 1.3 of the [Operator Development Toolchain Learning Environment Installation Guide](https://gitcode.com/Ascend/msot/blob/master/docs/en/quick_start/installation_guide.md) to reconfigure.

### Runtime Error When Compiling the Operator Invocation Program: fatal error: aclnn_add_custom.h: No such file or directory

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

During operator deployment, op_api/include/aclnn_add_custom.h was not deployed to the correct location, resulting in the header file not being found. One possible reason is that the environment variable `ASCEND_CUSTOM_OPP_PATH` exists in the environment, and its value is either incorrect or contains multiple colon-separated paths. However, when deploying the header file, it is only successfully copied to the first path, and subsequent directories are not deployed.

**Solution**

Delete the environment variable (execute `unset ASCEND_CUSTOM_OPP_PATH`), and then redeploy the operator.

### Runtime Error When Executing execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize

**Problem Symptom**

```text
execute_add_op: symbol lookup error: ./build/execute_add_op: undefined symbol: aclnnAddCustomGetWorkspaceSize
```

**Root Cause** 

After deploying the operator, the .so file was not added to the environment variable LD_LIBRARY_PATH as prompted in the output.

**Solution**

Follow step 3 in [2.3.3 Compiling and Deploying Operators](#233-compiling-and-deploying-operators) to reset the LD_LIBRARY_PATH environment variable.

### Runtime Error When Setting Breakpoints in msDebug: WARNING: Unable to resolve breakpoint to any actual locations

**Problem Symptom**

```text
(msdebug) b add_custom.cpp:23
Breakpoint 1: no locations (pending on future shared library load).
WARNING:  Unable to resolve breakpoint to any actual locations.
```

**Root Cause** 

The specified breakpoint line may be an empty line, a comment, or another line where a breakpoint cannot be set, or `/proc/debug_switch` was not set successfully. Refer to the next section for the reason.

**Solution** 

Check the source code file to confirm the actual line number of the code; follow [2.5.1 Enable Kernel Debug Switch](#251-enabling-kernel-debug-switch) to set `/proc/debug_switch` = 1 on the host machine (note: not inside the container) with root privileges.

### Runtime Error When Executing msDebug run: error: 'A' packet returned an error: 8

**Problem Symptom**

```text
error: 'A' packet returned an error: 8
```

**Root Cause**

The `/proc/debug_switch = 1` setting was not successfully applied. Verify whether it has been reset to 0 on the host machine. Alternatively, if you are operating within a container environment provided by a cloud service provider, even if `/proc/debug_switch` is successfully set and queried as 1 inside the container, this status may be false. For security reasons, the underlying host typically isolates the /proc directory through mechanisms such as copy-on-write (CoW), shadow files, or overlay mounts, causing the setting to not take effect.

**Solution**

Log in to the host machine (not inside the container) with root privileges, and set `/proc/debug_switch` = 1 as described in [2.5.1 Enable Kernel Debug Switch](#251-enabling-kernel-debug-switch). If the setting cannot be applied successfully, you must skip this tool experience.
