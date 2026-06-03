# Introduction

The MindStudio Operator Tools (msOT) operator development toolchain is dedicated to addressing key challenges in operator development. By providing capabilities such as efficient operator design, automatic development framework generation, comprehensive functional debugging, precise anomaly detection, and multi-dimensional performance tuning, it reduces the complexity of operator development and improves the delivery efficiency of high-performance operators.

<img src="../figures/readme/fullview.svg" width="1200"/>

## Feature Introduction

The operator development toolchain provides the following series of tools:

- msKPP (MindStudio-Kernel-Performance-Prediction)
Performance Prediction Tool: Supports inputting operator descriptions to predict the performance upper limit of an operator under a specific algorithm implementation. For details, see: [Operator Modeling Tool](https://gitcode.com/Ascend/mskpp/blob/master/docs/en/quick_start/mskpp_quick_start.md).
- msOpGen (MindStudio-Ops-Generator)
Project Generation Tool: An operator development efficiency improvement tool that provides template project generation capabilities to simplify project setup. For details, see: [Operator Project Generation Tool](https://gitcode.com/Ascend/msopgen/blob/master/docs/en/quick_start/msopgen_quick_start.md).
- msSanitizer (MindStudio-Sanitizer)
Anomaly Detection Tool: Provides memory, race condition, uninitialized access, and synchronization detection, supporting precise localization of memory issues in multi-core programs. For details, see: [Operator Detection Tool](https://gitcode.com/Ascend/mssanitizer/blob/master/docs/en/quick_start/mssanitizer_quick_start.md).
- msDebug (MindStudio-Debugger)  
Native Debugging Tool: Debugging in the native environment of the Ascend processor, supporting variable inspection, single-step execution, and on-device debugging. For details, see: [Operator Debugging Tool](https://gitcode.com/Ascend/msdebug/blob/master/docs/en/quick_start/msdebug_quick_start.md).
- msOpProf (MindStudio-Ops-Profiler)  
Performance Analysis Tool: Supports on-device and simulation data collection, and locates performance bottlenecks through the MindStudio Insight visualization tool. For details, see: [Operator Performance Tuning Tool](https://gitcode.com/Ascend/msopprof/blob/master/docs/en/quick_start/msopprof_quick_start.md).
- msKL (MindStudio-Kernel-Launcher)  
Quick Invocation Tool: Provides a Python interface for rapid Kernel code generation, compilation, and execution. For details, see: [Operator Kernel Lightweight Invocation](https://gitcode.com/Ascend/mskl/blob/master/docs/en/quick_start/mskl_quick_start.md).
- msTX (MindStudio Tools Extension Library)  
Tool Extension SDK: Introduces the msTX instrumentation API. It allows you to customize the collection time period or the start and end time points of key functions, identify information such as key functions or iterations, and quickly scope performance and operator issues. For detailed API introduction, see [Tool Extension SDK msTX](https://gitcode.com/Ascend/mstx/blob/master/docs/en/api_reference/mstx_api_reference.md).
