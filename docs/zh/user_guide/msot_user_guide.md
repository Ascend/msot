# msOT 工具选型指南

<br>

msOT 工具链包含多款专项工具，覆盖算子开发的各个阶段。面对具体任务时，精准选型往往比盲目尝试更具效率。

本文以 **”我要做什么”** 为导向，帮助您快速锁定最匹配的工具及直达入口。

<br>

## 场景化工具推荐

| 我要做什么 | 推荐工具 | 为什么推荐 |
|-----------|----------|------------|
| 我想在写完整代码前评估一个算子方案的性能上限 | [msKPP](https://gitcode.com/Ascend/mskpp) | 支持用算子描述和 DSL 建模，快速预估指令、搬运和流水开销 |
| 我想从算子定义快速生成 Ascend C 工程 | [msOpGen](https://gitcode.com/Ascend/msopgen) | 自动生成 Host 侧、Kernel 侧、CMake 和编译部署框架 |
| 我想快速下发运行 Kernel，验证功能是否正确 | [msKL](https://gitcode.com/Ascend/mskl) | 提供 Python 接口，便于快速调用 Kernel 和 Tiling 函数 |
| 我想检测内存越界、未初始化、竞争或同步错误 | [msSanitizer](https://gitcode.com/Ascend/mssanitizer) | 面向 Ascend C 算子的运行时异常检测，可定位到源码调用栈 |
| 我想像调试 CPU 程序一样给 NPU 算子打断点、看变量 | [msDebug](https://gitcode.com/Ascend/msdebug) | 支持上板断点、单步、变量、寄存器、内存和调用栈查看 |
| 我想采集算子真实运行性能数据并定位瓶颈 | [msOpProf](https://gitcode.com/Ascend/msopprof) | 支持上板与仿真采集，可生成多维性能数据并配合 Insight 可视化 |
| 我想对关键函数、迭代或自定义阶段打点分析 | [msTX](https://gitcode.com/Ascend/mstx) | 提供扩展 SDK，可标记自定义采集区间，辅助性能和问题定界 |
