# msOT Tool Selection Guide

<br>

The msOT toolchain includes multiple dedicated tools covering every stage of operator development. For a specific task, choosing the right tool is often more efficient than trying tools blindly.

This guide is organized around **"what you want to do"** to help you quickly identify the best-matched tool and its direct entry point.

<br>

## Scenario-Based Tool Recommendations

| What You Want to Do | Recommended Tool | Why It Is Recommended |
|-----------|----------|------------|
| You want to evaluate the performance ceiling of an operator solution before writing the complete code. | [msKPP](https://gitcode.com/Ascend/mskpp/blob/26.1.0/README.md) | Supports modeling with operator descriptions and DSL to quickly estimate instruction, data movement, and pipeline overheads. |
| You want to quickly generate an Ascend C project from an operator definition. | [msOpGen](https://gitcode.com/Ascend/msopgen/blob/26.1.0/README.md) | Automatically generates the host-side code, kernel-side code, CMake files, and the compilation and deployment framework. |
| You want to quickly deploy and run a Kernel to verify that the functionality is correct. | [msKL](https://gitcode.com/Ascend/mskl/blob/26.1.0/README.md) | Provides a Python interface for quickly calling Kernel and Tiling functions. |
| You want to detect memory out-of-bounds access, uninitialized memory, race conditions, or synchronization errors. | [msSanitizer](https://gitcode.com/Ascend/mssanitizer/blob/26.1.0/README.md) | Provides runtime anomaly detection for Ascend C operators and can locate the source code call stack. |
| You want to set breakpoints and inspect variables in NPU operators just like debugging a CPU program. | [msDebug](https://gitcode.com/Ascend/msdebug/blob/26.1.0/README.md) | Supports on-device breakpoints, single-stepping, and viewing variables, registers, memory, and the call stack. |
| You want to collect real runtime performance data of operators and locate bottlenecks. | [msOpProf](https://gitcode.com/Ascend/msopprof/blob/26.1.0/README.md) | Supports on-device and simulation-based collection, generates multi-dimensional performance data, and integrates with Insight for visualization. |
| You want to add trace points to analyze key functions, iterations, or custom stages. | [msTX](https://gitcode.com/Ascend/mstx/blob/26.1.0/README.md) | Provides an extension SDK for marking custom collection intervals to help with performance analysis and problem isolation. |
