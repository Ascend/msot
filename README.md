# MindStudio Operator Tools

<br>

## 最新消息

* [2025.12.30]：MindStudio Operator Tools 项目首次上线 

## 简介

MindStudio Operator Tools（msOT）算子开发工具链，致力于解决算子开发中的关键挑战。通过提供高效算子设计、开发框架自动生成、全面功能调试、精准异常检测与多维性能调优等能力，
降低算子开发复杂度，提升高性能算子的交付效率。

## 功能介绍

算子开发工具链提供以下系列化工具：

| 工具名称 | 功能简介 | 源码仓库 |
| --- | --- | :---: |
| **msKPP** | **【性能预测】** 支持输入算子描述，预测算子在特定算法实现下的性能上限。 | [点击查看](https://gitcode.com/Ascend/mskpp) |
| **msOpGen** | **【工程生成】** 算子开发效率提升工具，提供模板工程生成能力，简化工程搭建。 | [点击查看](https://gitcode.com/Ascend/msopgen) |
| **msSanitizer** | **【异常检测】** 提供内存、竞争、未初始化及同步检测，支持多核程序内存问题的精准定位。 | [点击查看](https://gitcode.com/Ascend/mssanitizer) |
| **msDebug** | **【原生调试】** 基于昇腾处理器的原生环境调试，支持变量查看、单步执行及上板调试。 | [点击查看](https://gitcode.com/Ascend/msdebug) |
| **msOpProf** | **【性能分析】** 支持上板与仿真数据采集，通过 MindStudio Insight 可视化工具定位性能瓶颈。 | [点击查看](https://gitcode.com/Ascend/msopprof) |
| **msKL** | **【快捷调用】** 提供 Python 接口，快速实现 Kernel 的代码生成、编译及下发运行。 | [点击查看](https://gitcode.com/Ascend/mskl) |

## 快速入门

以简单的加法算子开发为例，贯穿算子开发全流程，10分钟快速体验msKPP(设计)、msOpGen(开发)、msSanitizer(检测)、msDebug(调试)、msOpProf(调优)工具的核心功能。    
详细操作步骤请参见 [《算子开发工具链快速入门》](docs/zh/quick_start/op_tool_quick_start.md)。

## 安装指南

介绍 msOT 工具的环境依赖与安装方法，具体请参见 [《msOT安装指南》](./docs/zh/install_guide/msot_install_guide.md)。

## 使用指南

各工具的详细使用说明请查阅其源码仓库中的 README 文件，仓库地址详见 [功能介绍](#功能介绍) 表格最后一列。

## 贡献指南

贡献流程详见 [《msOT 贡献流程说明》](./docs/zh/common/contribute_workflow.md)。  

## License

许可条款详见 [《msOT License声明》](./docs/zh/common/license_notice.md)。  

## 免责声明

免责条款详见 [《msOT 免责声明》](./docs/zh/common/disclaimer.md)。  

## 建议与交流

欢迎大家为社区做贡献。如果有任何疑问或建议，请提交 [Issues](https://gitcode.com/Ascend/msot/issues)，我们会尽快回复。感谢您的支持。

## 致谢

本工具由华为公司的下列部门贡献：   

- 计算产品线   

感谢来自社区的每一个PR，欢迎贡献。
