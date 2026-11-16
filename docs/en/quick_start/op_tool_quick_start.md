# Operator Development Toolchain Quick Start

<br>

## 1. Overview

The MindStudio operator development toolchain provides tools for the entire operator development lifecycle. This tutorial walks you through developing a simple addition operator so that you can experience the efficiency and convenience of the toolchain.

**Learning Roadmap (The core operations take only 10 minutes, with commands ready to copy and paste)**
> **Recommended order**: Step 1 is required. After completing it, you can try Step 2 or Step 3. Steps 4, 5, and 6 depend on the project generated in Step 3, but are otherwise independent and can be explored as needed.

| Step | Phase | Core Tool | Measured Hands-on Time | Suggested Background Reading Time |
| :---: | :---: | :--- | :---: | :---: |
| **1** | **Environment Preparation** | `CANN container image` | 3 minutes | 5 minutes |
| **2** | **Operator Design** | `msKPP` | 30 seconds | 5 minutes |
| **3** | **Project Development** | `msOpGen` | 1 minute | 20 minutes |
| **4** | **Anomaly Detection** | `msSanitizer` | 1 minute | 10 minutes |
| **5** | **Native Debugging** | `msDebug` | 1 minute | 10 minutes |
| **6** | **Performance Tuning** | `msOpProf` | 1 minute | 10 minutes |

## 2. Procedure

### 2.1 [Environment] Essential Environment Preparation (Mandatory Prerequisite)

🛑 **This section is a mandatory prerequisite. Skipping it will cause many subsequent operations to fail.**
This tutorial **supports only** standardized CANN container environments. Bare-metal, virtual machine, or other non-standard container deployments are not supported.

#### 2.1.1 Installing the CANN Container Environment

**Complete the environment installation strictly according to the following guide:**  
👉 **[Ascend AI Operator Development Toolchain Learning Environment Installation Guide](installation_guide.md)**

> **Estimated time for an environment with public network access: about 3 minutes (the exact time depends on network conditions)**  
> After the installation is complete, you will obtain a standardized container environment with all operator tools, sample code, and dependent libraries preinstalled.

#### 2.1.2 Checking the Environment

Before starting the hands-on steps, run the following commands in Bash inside the container, with the CANN environment loaded, to set the variable and check the environment:

```bash
source ~/ot_demo/msot/example/quick_start/scripts/set_chip_soc_env.sh &&
bash ~/ot_demo/msot/example/quick_start/scripts/check_env.sh --task core
```

The message `Environment check successful, summary 0 failure(s).` indicates that the check passed.

🚀 **Run all subsequent steps inside the container. Follow the sections in order when working through the complete tutorial, because later steps reuse artifacts produced earlier.**

### 2.2 [Design] Operator Modeling Design (msKPP)

Start by designing the operator algorithm. msKPP provides fast performance modeling to estimate performance without executing the operator on hardware and assess the feasibility of an implementation. Follow these steps to use the tool:

> [!NOTE]
> **msKPP Tool Principles**
>
> msKPP includes Python libraries designed for Ascend. Import the relevant modules, then write and run a Python script to generate performance analysis files and modeling results.

#### 2.2.1 Checking the Environment

The msKPP tool in this tutorial **supports only Ascend 910B-series chips**. Run the following command to check the chip type:

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/check_env.sh --task mskpp
```

The message `Environment check successful` indicates that the check passed and you can continue. Otherwise, switch to an environment with an Ascend 910B-series chip or skip this section.

#### 2.2.2 Developing the Modeling Script

1. Prepare the workspace and modeling sample.

    ```bash
    bash ~/ot_demo/msot/example/quick_start/scripts/prepare_sample.sh --sample mskpp --dest ~/ot_demo/workspace/mskpp
    cd ~/ot_demo/workspace/mskpp
    ```

    The message `Prepare sample successful` indicates success. This quick start focuses on tool usage and provides a sample script; its path is printed in the log. For actual development, implement or edit the script to meet your requirements.

> [!NOTE]
> **Background (Optional): The msKPP Domain-Specific Language (DSL)**
>
> These libraries and interfaces form a DSL designed for Ascend performance modeling. Using them requires familiarity with their APIs in addition to general Python syntax, but you can get started with a brief introduction.
>
> A typical workflow imports `Tensor`, `Chip`, and the required instructions, such as `vadd`, enters the operator implementation context using a `with` statement, and creates tensors to perform the operations. See the sample script comments for details and the [msKPP API Reference](https://gitcode.com/Ascend/mskpp/blob/master/docs/en/api_reference/mskpp_api_reference.md) for other instruction interfaces.

#### 2.2.3 Executing Performance Modeling

Run the following command to execute the Python script and start performance modeling:

```bash
python3 mskpp_demo.py
```

The message `MSKPP modeling completed successfully` indicates success. A result directory named `MSKPP{timestamp}` is automatically created in the current directory. See the log for its actual path.

#### 2.2.4 Viewing Modeling Results

The following are examples of some generated result files:

```text
MSKPP{timestamp}/
├── Instruction_statistic.csv
├── Pipe_statistic.csv
└── trace.json
```

Taking `Instruction_statistic.csv` as an example, its content is as follows:

| Instruction  | Duration(us) | Cycle | Size(B) | Ops  |
|:--------------:|:--------------:|:-------:|:---------:|:------:|
| MOV-GM_TO_UB |    0.3081    |  570  |  6144   |  -   |
|     VADD     |    0.0135    |  25   |    -    | 1536 |
| MOV-UB_TO_GM |    0.4254    |  787  |  3072   |  -   |

From the above content, it can be seen that MOV-UB_TO_GM (moving from UB to GM) has the longest duration and the highest number of instruction cycles, making it the critical path that requires focused attention during performance optimization. In actual development, if such memory transfer time is found to account for an excessively high proportion, priority should be given to optimizing data reuse (Tiling) or using more efficient transfer instructions.

### 2.3 [Development] Building the Operator Project (msOpGen)

After designing the algorithm, implement the operator. Operator projects typically contain substantial framework code. msOpGen generates the complete project framework so that you can focus on the core algorithm instead of repetitive project setup and build configuration. Follow these steps to use the tool:

#### 2.3.1 Generating Project Framework

1. Prepare the workspace and msOpGen input configuration file.

    Run the following script to create the `src` subdirectory and prepare the operator definition configuration file:

    ```bash
    bash ~/ot_demo/msot/example/quick_start/scripts/prepare_sample.sh --sample opgen --dest ~/ot_demo/workspace/src
    cd ~/ot_demo/workspace/src/
    ```

    The message `Prepare sample successful` indicates success. This quick start provides a sample operator definition JSON file so that you can focus on tool usage. Its path is printed in the script log. For actual development, implement or edit the configuration to meet your requirements.

    > [!NOTE]
    > **Background (Optional): The msOpGen Input Configuration File**
    >
    > The JSON file defines structured information about the operator, including its name, inputs, and outputs. It is comparable to a C function declaration that specifies the function name, input parameters, and return types.
    >
    > For example, `msopgen_demo.json` defines the operator name and the names, types, and data layouts of its inputs and outputs. The tool generates the function declaration and an empty implementation containing only the name, parameters, and return value. You must implement the function body for your requirements.

2. Generate the operator code framework.

    Run the following command to generate an Ascend C operator project. `-lan cpp` specifies Ascend C code, and `-c` specifies the chip SoC model:

    ```bash
    msopgen gen -i msopgen_demo.json -c ai_core-ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} -lan cpp -out AddCustom
    ```

    The message `Generation completed` indicates success. For detailed parameter descriptions, refer to the *User Guide* in the [msOpGen repository](https://gitcode.com/Ascend/msopgen).

    > [!CAUTION]
    > The generated operator implementation is empty and cannot perform addition. Implement the core logic as described in [2.3.2 Implementing Core Logic](#232-implementing-core-logic) before running the operator.

3. View the generated results.

    > [!NOTE]
    > **Background (Optional): Key Concepts**
    >
    > Host Side: Code running on the CPU, responsible for data preprocessing, task scheduling, and operator invocation.   
    > Kernel Side: Code running on the NPU, responsible for executing the actual large-scale parallel computation logic.   
    > Tiling: Partitioning large-scale data into blocks to improve Local Memory utilization and optimize memory access efficiency.

    The generated project may look large and complex, but you **only need to focus on the three C++ files marked as [User Extension Points]**. The remaining files provide framework code and do not need to be inspected or modified unless required:

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

> [!NOTE]
> **Background (Optional): How the Operator Source Files Work Together**
>
> `op_host/add_custom.cpp`: Implements the Tiling computation logic on the Host side and operator prototype registration.  
> `op_kernel/add_custom_tiling.h`: Defines the data structure for the Tiling strategy.  
> `op_kernel/add_custom.cpp`: Implements the specific computation logic of the addition operator on the Kernel side (GM→UB→vector addition→UB→GM).   
> If you need a deeper understanding of the functions and collaboration mechanisms of the three aforementioned files, in addition to referring to the code comments, you are advised to read the <a href="https://www.hiascend.com/developer/blog/details/0239124507827469022" target="_blank">Ascend C Programming Introductory Tutorial (Pure Practical Information)</a> in detail.  
> The helper below preserves the SoC from the generated Host file. It does not guess the current chip again or use a temporary cache shared across projects.

Implement the algorithm in the three [User Extension Point] files. This tutorial uses the published addition implementation: the helper validates a supported, unedited generated template, prepares the three C++ files and the sibling `caller` sample, and records a project-local normal teaching baseline. It does not generate, build, deploy or run the project. Actual development requires your own implementation:

```bash
cd ~/ot_demo/workspace/src/AddCustom/
bash ~/ot_demo/msot/example/quick_start/scripts/prepare_add_demo.sh --project .
```

#### 2.3.3 Compiling and Deploying Operators

1. Compile the operator.

    Run the build script. Upon success, an operator deployment package in `.run` format will be generated in the `build_out` directory:

    ```bash
    bash ./build.sh
    ```

2. Deploy the operator.

    > [!NOTE]
    > **What Does Operator Deployment Mean?**
    >
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

> [!CAUTION]
> **Notes on NPU Device Selection**
>
> The following `run.sh` script runs the operator. By default, it uses the results of `npu-smi info` to select the first idle NPU in the displayed order.
> To specify an NPU, use its sequence number from the device information returned by `npu-smi info` (range: [0, number of NPUs - 1]). For example: `bash ./run.sh 2`.

Execute the operator invocation project to verify the operator functionality (this example executes 1.0 + 2.0, with an expected result of 3.0):

```bash
cd ~/ot_demo/workspace/src/caller
bash ./run.sh
```

If the following content is output and the result is 3.0, it indicates that the operator has been successfully loaded and calculated correctly:

```text
result is:
3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 3.0 
test pass
```

If errors such as the following occur, use the troubleshooting table below:

```text
aclrtSetDevice failed. ERROR: xxxxxx
Init acl failed. ERROR: 1
```

| Symptom | Possible Cause | Action |
|------|----------|----------|
| No result for more than 30 seconds | The NPU is busy. | Press Ctrl+C to stop, select another idle NPU, and retry. See "Notes on NPU Device Selection" above for how to specify an NPU. |
| ACL errors such as those above | An NPU hardware or driver problem; an unavailable or inaccessible `/dev/hisi_hdc` device; or insufficient system resources such as memory. | Resolve the device problem or use a healthy NPU and retry. See the [ACL Error Code Table](https://www.hiascend.com/document/detail/en/CANNCommunityEdition/850/API/appdevgapi/aclcppdevg_03_1345.html) for error code details. |

### 2.4 [Detection] Operator Anomaly Detection (msSanitizer)

After developing the operator, use msSanitizer to detect serious runtime defects such as out-of-bounds memory accesses, race conditions, uninitialized variables, and synchronization errors:

#### 2.4.1 Preparing Detection Options and Source Code

Configure `-sanitizer` at the beginning of the kernel-side `CMakeLists.txt` to enable instrumentation, and specify `--fixture oob` to prepare teaching source code containing an out-of-bounds access:

```bash
cd ~/ot_demo/workspace/src/AddCustom
bash ~/ot_demo/msot/example/quick_start/scripts/prepare_mode.sh --project . --mode sanitizer --fixture oob
```

The message `Successfully prepared sanitizer mode` indicates that sanitizer mode was prepared successfully.

> [!NOTE]
> The teaching defect doubles the copy length in an `AscendC::DataCopy` call (`2 * this->tileLength`). This causes an access beyond the GM allocation for `xGm`, triggering an "illegal read" error.

#### 2.4.2 Recompiling and Deploying

```bash
bash ./build.sh
bash ./build_out/custom_opp_openEuler_aarch64.run
```

#### 2.4.3 Running Memory Checking

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

> [!NOTE]
> An operator may appear to run successfully despite memory errors. This illustrates the value of the tool: memory defects may be intermittent or remain silent without an obvious failure (silent failure). A crash may occur only under certain conditions, so functional output alone is not sufficient to identify the problem.

#### 2.4.4 Restoring the Normal Sample

Run the following command to restore the sample source files and kernel-side CMake configuration. The deployed operator is unchanged; explicitly rebuild and redeploy it in the next section:

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/restore_demo.sh --project ~/ot_demo/workspace/src/AddCustom
```

The message `Successfully restored source files` indicates success.

### 2.5 [Debugging] Breakpoint Debugging of Operator Code (msDebug)

If the operator behaves unexpectedly, use msDebug to set breakpoints and investigate the problem:

#### 2.5.1 Enabling Kernel Debug Switch

Check whether the kernel debug switch `debug_switch` is enabled:

```bash
cat /proc/debug_switch
```

If the reported value is not `1`, open a new **host terminal** and run the following commands as root:

```bash
echo 1 > /proc/debug_switch
cat /proc/debug_switch
```

If `cat /proc/debug_switch` reports `1`, the switch is enabled. If it cannot be enabled, skip the msDebug exercise in this section.

> [!CAUTION]
> `/proc/debug_switch` is a virtual file under `/proc`, provided by the Ascend driver to control whether msDebug can debug operator kernels running on the NPU.
>
> Container mounts and permission restrictions can affect access to this interface. Have an administrator configure and verify the switch on the host. An unavailable debug environment may cause errors during debugging, such as `'A' packet returned an error: 8`; this error alone does not identify the cause.

#### 2.5.2 Modifying Compilation Options and Redeploying

1. Modify compilation options.

    Prepare debug mode by adding `-g -O0` at the beginning of the kernel-side `CMakeLists.txt` to enable debug information and disable optimization:

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    bash ~/ot_demo/msot/example/quick_start/scripts/prepare_mode.sh --project . --mode debug
    ```

    The message `Successfully prepared debug mode` indicates success.

2. Recompile and deploy the operator.

    ```bash
    bash ./build.sh
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

#### 2.5.3 Setting Debug Environment Variables

Source the following script to set `LAUNCH_KERNEL_PATH`, specifying the operator object file to load for debugging symbols:

```bash
source ~/ot_demo/msot/example/quick_start/msdebug/set_kernel_obj_env.sh
```

#### 2.5.4 Breakpoint Debugging and Variable Inspection

1. Start the debugger

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msdebug execute_add_op
    ```

2. Set a breakpoint.

    After the `(msdebug)` prompt appears, run the following command to set a breakpoint at line 34 of `add_custom.cpp`:

    ```text
    b add_custom.cpp:34
    ```

    A message beginning with `Breakpoint 1: XXX` indicates that the breakpoint was set.

    > [!CAUTION]
    > If `/proc/debug_switch` is not enabled on the host, NPU kernel debugging may fail when you run the program, for example with `'A' packet returned an error: 8`. Successfully resolving a breakpoint does not by itself confirm that runtime debugging is available.

3. Run the operator.

    Run the following command to start the program and wait for it to hit the breakpoint:

    ```text
    run
    ```

    If the following information is displayed, the breakpoint has been hit successfully (the display may vary slightly between versions, which does not affect learning how to use the tool):

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

#### 2.5.5 Restoring Debug Preparation

Run the following command to restore the sample source files and kernel-side CMake configuration. The deployed operator is unchanged; explicitly rebuild and redeploy it in the next section:

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/restore_demo.sh --project ~/ot_demo/workspace/src/AddCustom
```

The message `Successfully restored source files` indicates success.

### 2.6 [Tuning] Analyzing Operator Performance (msOpProf)

If operator performance does not meet expectations, use msOpProf to collect runtime performance data for detailed analysis and optimization across Ascend hardware platforms.

#### 2.6.1 Modifying Compilation Options and Recompiling/Deploying

1. Modify compilation options.

    Prepare profile mode by adding `-g` at the beginning of the kernel-side `CMakeLists.txt` to enable symbol information while preserving the project's existing optimization policy:

    ```bash
    cd ~/ot_demo/workspace/src/AddCustom
    bash ~/ot_demo/msot/example/quick_start/scripts/prepare_mode.sh --project . --mode profile
    ```

    The message `Successfully prepared profile mode` indicates success.

    > [!NOTE]
    > **Background (Optional): Why Different Tools Use Different `-O` Optimization Levels**
    >
    > `-O0` disables most compiler optimizations, making execution during debugging more closely follow the source structure and simplifying breakpoint setting, single-stepping, and variable inspection. Debug symbols must still be generated using `-g`.
    >
    > `-O2` enables more compiler optimizations. When single-stepping in a debugger, execution may skip source lines, multiple source lines may map to the same execution location, or functions may be inlined. Performance may differ severalfold from an `-O0` build. Performance analysis should use the same optimization configuration as the production deployment, typically `-O2` or the project's default optimization configuration. Avoid retaining debugging mode's `-O0`, which may cause the collected results to differ from actual production performance.

2. Recompile and deploy the operator.

    ```bash
    bash ./build.sh
    bash ./build_out/custom_opp_openEuler_aarch64.run
    ```

#### 2.6.2 Starting On-Board and Simulation Collection

> [!NOTE]
> **Differences Between Simulation and On-Board Profiling**
>
> Simulation provides stable, preliminary analysis of instruction traces and code hotspots without requiring a physical NPU, but has limited accuracy for hardware-dependent behavior such as memory access latency and bandwidth bottlenecks.
>
> On-board profiling runs the operator on a physical device to capture actual execution time, pipe utilization, memory bandwidth, cache behavior, and other hardware characteristics.
>
> Combine both methods for efficient, comprehensive performance analysis.

1. Perform simulator performance profiling.

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msopprof simulator --soc-version=Ascend${MY_STUDY_VAR_CHIP_SOC_TYPE} --output=./msopprof_output_sim ./execute_add_op
    ```

    The message `Op profiling finish.` indicates success. See the path following `Profiling results saved in` in the log for the results.

2. Perform on-board performance profiling.

    ```bash
    cd ~/ot_demo/workspace/src/caller/build
    msopprof --output=./msopprof_output_npu ./execute_add_op
    ```

    The message `Op profiling finish.` indicates success. See the path following `Profiling results saved in` in the log for the results.

#### 2.6.3 Viewing Performance Data Results

The tool generates `.csv` and `.bin` result files in the directory specified by `--output`:

- CSV files   

  For example, `MemoryUB.csv` contains the following information. The task is divided evenly among 8 blocks, all scheduled on vector cores. Block 0 has higher bandwidth (1.02 GB/s) than Block 1 (0.77 GB/s). A large difference may indicate an opportunity for optimization:

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

- BIN files

  Open these files in MindStudio Insight for graphical performance views, such as compute and memory heatmaps, cache heatmaps, and code hotspot maps.

  > [!NOTE]
  > 
  > To experience visual chart viewing, refer to the <a href="https://gitcode.com/Ascend/msinsight/blob/master/docs/en/install_guide/mindstudio_insight_install_guide.md" target="_blank">MindStudio Insight Tool Documentation</a> to install the Insight tool.

#### 2.6.4 Restoring Profile Preparation

Restore the sample source configuration. The deployed operator and profiling results are unchanged. To run the restored normal operator, explicitly rebuild and redeploy it:

```bash
bash ~/ot_demo/msot/example/quick_start/scripts/restore_demo.sh --project ~/ot_demo/workspace/src/AddCustom
```

### 2.7 [Completion] Advanced Learning Path

Congratulations on completing the introductory experience of the Operator Development Toolchain.

At this point, you have fully walked through the entire operator development process of "Design → Develop → Detect → Debug → Tune" and have practically experienced the basic usage of the following five core tools:

| Tool | Core Capabilities You Have Mastered |
| ----------- | --------------------------------- |
| **msKPP** | Write DSL scripts for operator performance modeling and estimate performance bottlenecks without hardware. |
| **msOpGen** | Automatically generate operator project frameworks based on configuration files, and complete compilation, deployment, and functional verification. |
| **msSanitizer** | Instrument operators to locate runtime defects such as out-of-bounds memory accesses in the source code. |
| **msDebug** | Start breakpoint debugging, set breakpoints in NPU operator code, and inspect variables. |
| **msOpProf** | Collect performance data through both on-board and simulation modes, and analyze the execution efficiency of each Block. |

If you want to continue with advanced experience, you can refer to the following steps:

**Step 1: Consolidating the Foundation: Independently Developing a New Operator**  

Refer to the `AddCustom` example in this tutorial and try to independently implement a subtraction operator (`SubCustom`) or multiplication operator (`MulCustom`), focusing on: differences in Tiling strategy design, the use of different computation instructions (such as `vsub`, `vmul`), and the end-to-end compilation and deployment process.

**Step 2: Diving into Tools: Mastering the Advanced Features of Each Tool**  

This tutorial only covers the introductory usage of each tool. Each tool offers richer advanced capabilities. You are advised to access the *User Guide* of the corresponding repository as needed for in-depth learning:

| Tool | Advanced Capabilities |
|------|--------------|
| [msKPP](https://gitcode.com/Ascend/mskpp/blob/master/docs/en/user_guide/mskpp_user_guide.md) | Modeling cache hit rates and on-the-fly conversion, comparing the performance of multiple Tiling strategies, and more. |
| [msOpGen](https://gitcode.com/Ascend/msopgen/blob/master/docs/en/user_guide/msopgen_user_guide.md) | Complex operator template customization, project generation for multi-input multi-output operators, and so on. |
| [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/master/docs/en/user_guide/mssanitizer_user_guide.md) | More detection modes such as race condition detection, synchronization anomaly diagnosis, and uninitialized variable checking. |
| [msDebug](https://gitcode.com/Ascend/msdebug/blob/master/docs/en/user_guide/msdebug_user_guide.md) | Advanced debugging techniques such as memory viewing, core switching, and parsing Core dump files. |
| [msOpProf](https://gitcode.com/Ascend/msopprof/blob/master/docs/en/user_guide/msopprof_user_guide.md) | Visual performance analysis combined with [MindStudio Insight](https://gitcode.com/Ascend/msinsight/blob/master/docs/en/install_guide/mindstudio_insight_install_guide.md), including compute memory heatmaps, cache heatmaps, and code hotspot maps. |

**Step 3: Applying the Toolchain to Real Workloads: From Learning to Production**

Study the [Ascend C Programming Guide (Official Tutorial)](https://www.hiascend.com/zh/ascend-c?utm_source=cann&utm_medium=article&utm_campaign=alll) to build a systematic understanding of multi-level pipelining, data layouts, and memory management. Then apply the toolchain to developing and tuning operators for real workloads, progressing from prototype validation to production delivery.

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

After deployment, the directory containing the operator's `.so` library was not added to `LD_LIBRARY_PATH` as instructed in the deployment output.

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

The specified line may be blank, contain a comment, or otherwise have no executable code where a breakpoint can be resolved. Also check the debug switch and runtime prerequisites described in the next section.

**Solution**

Check the source code file to confirm the actual line number of the code, and follow [2.5.1 Enabling Kernel Debug Switch](#251-enabling-kernel-debug-switch) to set `/proc/debug_switch` = 1 on the host machine (note: not inside the container) with root privileges. If the setting cannot be applied successfully, you can only skip this tool experience.

### 3.4 Runtime Error When Executing msDebug `run`: error: `'A' packet returned an error: 8`

**Problem Symptom**

```text
error: 'A' packet returned an error: 8
```

**Root Cause**

This error indicates that a debug launch request failed. Possible causes include `/proc/debug_switch` not being enabled, restricted device access, or incompatibility between the driver and debugging components.

**Solution**

Container mounts and permission restrictions may affect access to and modification of `/proc/debug_switch`. An administrator should configure the switch on the host and confirm that its state is `1`. If the switch is enabled but debugging still fails, use the relevant logs to further investigate device access permissions and compatibility between the driver and debugging components.
