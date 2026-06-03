# MindStudio Operator Tools Release Notes

## Version Compatibility

### Product Version Information

| Product Name | Product Version | Version Type |
|------|-------|------|
| msOT | 26.0.0 | Internal Beta |
| msOT | 8.3.0 | Official Release |

### Related Product Version Compatibility

| msOT Version | CANN Version | Python Version
|----------|-----------------|----------
| 26.0.0 | 9.0.0 and above recommended | Python 3.11 and above recommended
| 8.3.0 | 8.2.RC1 and above | Python 3.11 and above recommended 

## Version Compatibility

### 26.0.0

1. Adapted to changes in BiSheng compiler compilation options.
2. Adapted to multiple new chip specifications and compatible with CANN chip identifier changes.

## Feature Change Description

### 26.0.0

#### 1. New Feature Description

##### msDebug

Feature Category:

1. Supported on-board debugging without setting the kernel object path
2. Supported skipping element count display when reading memory
3. Supported debugging for shared_memory operator scenarios
4. Supported coredump debugging and on-board debugging for operators compiled with asc
5. Supported variable logging for kernel struct variables passed from the host
6. Added call stack backtracking for non-inline compilation in coredump parsing

Build and Release:

1. Modified the minimum permission requirement for folders during root user installation to 700
2. Fixed the issue where UT compilation failed on GCC 7/12
3. Unified the naming of installation packages
4. Resolved the issue of incorrect libtinfo dynamic library path during compilation
5. Added libform.so.5 as a deliverable to resolve dependency on this file during builds in certain environments
6. Added support for Unix Makefiles builds

Documentation:

1. Comprehensively optimized and restructured documentation to improve usability

##### msOpProf

Feature Category:

- New Features:

1. Added performance tuning support for the shmem operator library and the asc operator library.
2. Added performance analysis capability for the custom compute-fusion framework. A compute pipeline graph can be generated via AscendC API instrumentation.
3. Supports refined analysis of Scalar performance data, enabling identification of specific blocking locations in Scalar unit time consumption. Related performance metrics have been expanded in the performance data file and the compute memory heatmap - memory load analysis.
4. Supports SIMT VF instruction stall analysis and register utilization display. Related performance metrics have been expanded in the on-board code hotspot map.
5. Supports SIMT VF instruction issue efficiency metric statistics and load balancing analysis. Related performance metrics have been expanded in the compute memory heatmap - inter-core load analysis.

- Optimizations:

1. Optimized help information display based on supported features of different chips.
2. Optimized the theoretical bandwidth values and performance indicator formulas for some chip models.
3. Optimized the lane sorting and instruction color division of the simulation pipeline graph.
4. Optimized the instruction information sorting of the code heatmap.
5. Enhanced software security by changing the permissions and ownership of build artifacts and on-disk files.

Build and Release:

1. Optimized the dependency repository download function, achieving a 10x increase in download speed.
2. Added a debug compilation option to support breakpoint debugging of compiled artifacts.
3. Changed the installation package name to mindstudio-opprof_linux.run.

Documentation:

1. Refreshed README links and added other documents and images, such as user guides, to the docs repository.
2. Renamed the installation guide to msopprof_install_guide.md.
3. Modified and optimized the content of the installation guide and quick start guide. Added a dependency note for pigz in the installation documentation.

##### msSanitizer

Feature Category:

- Detection Features:

1. Supports out-of-bounds detection for LocalTensor in AscendC unary, binary computation, and data movement APIs.
2. Supports memory corruption detection between SIMT and Main-Scalar pipelines.
3. Supports competition detection among threads within a SIMTR VF.
4. Supports redundant SET_FLAG instruction detection.
5. Added extensive instrumentation and processing for intra-core and inter-core synchronization instructions, enhancing competition detection capabilities. The newly added instructions are as follows: SET_FLAG/WAIT_FLAG/SET_FLAGI/WAIT_FLAGI/HSET/HWAIT/GET_BUF/RLS_BUF.

- User Interface:

1. Kernel information is now displayed during the detection process, and a prompt is shown after detection to indicate whether any anomalies were found.
2. Added the --demangle command-line option to control the display format of function names in the user interface.
3. Supports fetching real-time register status at the start and checking register default values at the end of the program.

- Extended Capabilities:

1. On the kernel side, the mstx interface has added reporting interfaces for inter-core barrier and set_flag/wait_flag semantics.
2. The kernel-side mstx interface is now exposed through the sanitizer_report.h header file, allowing users to integrate it as needed.
3. The memory pool information reporting interface in mstx has removed the binding restriction between region and heap, supporting direct region registration.

Build and Release:

1. Added debug compilation capability, supporting VSCode breakpoint debugging.
2. Modified the minimum permission requirement for folders during root user installation to 700.
3. Resolved the UT compilation failure issue with newer GCC 11.x versions, adapting to GCC 11.x.
4. Adapted to the GCC 12.x changes in the CANN image.
5. Optimized UT dependency downloads, increasing speed by 10 times and completely resolving the probabilistic failure issue.
6. Enabled debug compilation mode by default for UT compilation.
7. Unification of installation package names.
8. Added the sanitizer_report.h header file to the package.

Documentation:

1. Comprehensively optimized and restructured the documentation to improve usability.

##### msOpGen

Feature Category:

1. Adapted to the new AscendC operator project.

#### II. Deletion Description

No relevant deletion description

#### III. Bugfix

##### msDebug

1. Fixed an issue where the finish command caused the tool to hang in certain scenarios.
2. Fixed an issue where the ascend info cores command echoed multiple `*` in mix operator scenarios.
3. Optimized the garbled display issue when printing `uint8_t *` variables such as gm using the var command.
4. Optimized error prompts for some features.

##### msSanitizer

1. Fixed the issue where simt ldk/stk instructions were not written to disk.
2. Fixed the issue where file paths were not normalized before use and header files were included in an improper order.
3. Fixed the issue where the simt UB range modeling was incorrect, which could cause the tool to miss UB out-of-bounds errors.
4. Fixed the issue where the command-line option name for call stack traceback did not conform to industry conventions, and updated the command-line option name.
5. Fixed the issue where the address space of the load/store instruction was INVALID.
6. Fixed the ND NZ API preprocessing error issue, which could cause false positives for out-of-bounds memory access.
7. Fixed the issue where the abnormal call stack for competition and synchronization detection did not mask the internal implementation of the AscendC API.
8. Fixed the issue where synchronization instructions were incorrectly used in the inter-thread stomp online detection algorithm.
9. Fixed the deadlock issue in the soft synchronization detection algorithm, which could cause missed detections in competition detection.
10. Fixed the false positive issue caused by the synchronization detection algorithm not being reset in multi-operator scenarios.
11. Corrected the parsing of LD/LD_IO/ST/ST_IO/STI_IO instructions, resolving the issue of missing misalignment detection logic.
12. Fixed the issue where the summary displayed incorrectly after operator detection completed.
13. Fixed the blockIdx function calculation error when linking mix operators.
14. Fixed the LOAD2D address overflow error that occurred when running operators after dynamic instrumentation on specific chips.
15. Fixed the issue where DataCopy instruction misalignment detection was reported repeatedly.
16. Fixed the issue where inconsistent gm addresses in the dual page table range caused false memory alarms.
17. Fixed the missed reporting of multi-thread race conditions in simt operators.
18. Fixed the modeling error issue of the get_buf rls_buf instruction.
19. Optimized the create_folder function to modify folder group and permissions only after the directory is created.
20. Fixed an issue where the tool exited prematurely in certain scenarios.
21. Fixed the issue of missed competition detection between pipe-s and other pipelines.

### 8.3.0

#### 1. New Feature Description

##### msDebug

Initial Release with the following features:

1. On-board debugging: Supports breakpoint display, variable logging, register logging, memory logging, code-line-level single-step debugging, core information display and switching, and call stack display.
2. Coredump file parsing: Supports call stack display, register display, and variable display.

##### msKL

Initial Release with the following features:

1. Provides tiling_func and get_kernel_from_binary interfaces, supporting calls to tiling functions in the msOpGen project and user-defined Kernel functions for convenient rapid debugging.
2. Provides a series of autotune interfaces, supporting code replacement, compilation, execution, and performance comparison for template library operators, facilitating efficient tuning.

##### msKPP

Initial Release. New features are as follows:

1. Operator feature modeling: Simulates operator time consumption based on the interfaces provided by msKPP.
2. Operator computation and transfer specification analysis: Generates transfer pipeline statistics files and instruction information statistics files, allowing you to view msKPP modeling results.
3. Ultimate performance analysis: Generates instruction pipeline graphs and instruction proportion pie charts, allowing you to view msKPP modeling results.
4. Preliminary operator tiling design: Enables quick screening of several optimal tiling strategies.

##### msOpGen

Initial release with the following new features:

1. Output the operator project based on the operator prototype definition.
2. Output the operator simulation pipeline graph file based on the dump data file generated by the performance simulation environment.
3. Operator project compilation and deployment.

##### msOpProf

Initial Release, with the following new features:

msOpProf Mode:

1. Compute and Memory Heatmap: Displays operator basic information, compute load analysis, and memory load analysis data by resource dimension, helping developers identify resource bottlenecks from a global perspective.
2. Roofline Bottleneck Analysis Graph: Constructs a performance model of the processor, then uses this performance model to quickly evaluate the theoretical performance limit of the operator, helping developers quickly identify bottleneck types.
3. Compute-Pipeline Graph (Compute-Pipeline Fusion Operator): Provides an intuitive view of compute-pipeline operation status and instruction time consumption, helping developers identify compute-pipeline bottlenecks. Supports performance tracing via the AscendC API to collect actual time consumption of code on operator blocks, used for compute-pipeline operator performance analysis and optimization.
4. Pipe Flow Graph: Provides an intuitive observation of the operation status of each Pipe of the operator.
5. Operator Code Heatmap: Supports viewing the mapping relationship between operator source code and instruction sets, time consumption, and other functions, helping developers identify hot code distribution and analyze the feasibility of hot function optimization.
6. Cache Heatmap: Visually presents the Cache heatmap, displaying corresponding instruction information to optimize the L2 Cache hit rate.
7. Performance Data File: Displays detailed operator performance data from multiple performance metric dimensions.

msOpProf simulator mode:

1. Instruction Pipeline Graph: Displays timing relationships at the instruction level and correlates with the call stack to quickly locate bottlenecks.
2. Operator Code Hotspot Map: Supports viewing the mapping relationship between operator source code and instruction sets, as well as time consumption, helping developers identify hotspot code distribution and analyze the feasibility of hotspot function optimization.
3. Memory Throughput Bandwidth Waveform: Supports statistical analysis of the memory bandwidth of operator MTE log paths over time, helping developers identify bandwidth usage at each stage of the operator and analyze the feasibility of bandwidth optimization.

##### msSanitizer

Initial Release, with the following new features:

1. Memory Detection: Detects memory anomalies such as out-of-bounds access and unaligned access in Global Memory and Local Memory.
2. Race Detection: Detects data race issues caused by concurrent memory access in parallel computing environments.
3. Uninitialized Detection: Detects memory read exceptions caused by using uninitialized variables.
4. Synchronization Detection: Detects unpaired SetFlag/WaitFlag instructions in Ascend C operators.

#### II. Deletion Description

No related deletion changes

#### III. Bugfix

No related bugfix changes
