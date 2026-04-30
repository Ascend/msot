# 简介

MindStudio Operator Tools（msOT）算子开发工具链，致力于解决算子开发中的关键挑战。通过提供高效算子设计、开发框架自动生成、全面功能调试、精准异常检测与多维性能调优等能力，降低算子开发复杂度，提升高性能算子的交付效率。

<img src="../figures/readme/fullview.svg" width="1200"/>

## 功能介绍

算子开发工具链提供以下系列化工具：

- msKPP（MindStudio-Kernel-Performance-Prediction）  
性能预测工具：支持输入算子描述，预测算子在特定算法实现下的性能上限。详细介绍请参见：《[算子建模工具](https://gitcode.com/Ascend/mskpp/blob/master/docs/zh/quick_start/mskpp_quick_start.md)》。
- msOpGen（MindStudio-Ops-Generator）  
工程生成工具：算子开发效率提升工具，提供模板工程生成能力，简化工程搭建。详细介绍请参见：《[算子工程生成工具](https://gitcode.com/Ascend/msopgen/blob/master/docs/zh/quick_start/msopgen_quick_start.md)》。
- msSanitizer（MindStudio-Sanitizer）  
异常检测工具：提供内存、竞争、未初始化及同步检测，支持多核程序内存问题的精准定位。详细介绍请参见：《[算子检测工具](https://gitcode.com/Ascend/mssanitizer/blob/master/docs/zh/quick_start/mssanitizer_quick_start.md)》。
- msDebug（MindStudio-Debugger）  
原生调试工具：基于昇腾处理器的原生环境调试，支持变量查看、单步执行及上板调试。详细介绍请参见：《[算子调试工具](https://gitcode.com/Ascend/msdebug/blob/master/docs/zh/quick_start/msdebug_quick_start.md)》。
- msOpProf（MindStudio-Ops-Profiler）  
性能分析工具：支持上板与仿真数据采集，通过 MindStudio Insight 可视化工具定位性能瓶颈。详细介绍请参见：《[算子性能调优工具](https://gitcode.com/Ascend/msopprof)》。
- msKL（MindStudio-Kernel-Launcher）  
快捷调用工具：提供 Python 接口，快速实现 Kernel 的代码生成、编译及下发运行。详细介绍请参见：《[算子 Kernel 轻量化调用](https://gitcode.com/Ascend/mskl/blob/master/docs/zh/quick_start/mskl_quick_start.md)》。
- msTX（MindStudio Tools Extension Library）  
工具扩展SDK：介绍msTX打点接口。可以自定义采集时间段或者关键函数的开始和结束时间点，识别关键函数或迭代等信息，对性能和算子问题快速定界。接口详细介绍请参见《[工具扩展SDK msTX](https://gitcode.com/Ascend/mstx/blob/master/docs/zh/api_reference/README.md)》。
