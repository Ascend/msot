# MindStudio Operator Tools

<br>

## 最新消息
* [2025.12.30]：MindStudio Operator Tools项目首次上线 

## 简介
MindStudio Operator Tools（msOT）算子开发工具链，旨在应对算子开发中的核心挑战。通过提供高效的算子设计、自动化开发框架生成、全面的功能调试、精准的异常检测以及多维度的性能调优等能力，
帮助开发者降低开发复杂度，快速交付高性能算子。

## 功能介绍
算子开发工具链提供如下系列化工具，旨在高效解决算子开发与优化过程中的各类典型场景的问题：
| 工具名称 | 功能简介 | 源码仓库 |
| --- | --- | :---: |
| **msKPP** | **【性能预测】** 支持输入算子表达，预测算子在特定算法实现下的性能上限。 | [点击查看](https://gitcode.com/Ascend/mskpp) |
| **msOpGen** | **【工程生成】** 算子开发效率提升工具，提供模板工程生成能力，简化工程搭建。 | [点击查看](https://gitcode.com/Ascend/msopgen) |
| **msSanitizer** | **【异常检测】** 提供内存、竞争、未初始化及同步检测，支持多核程序内存问题精准定位。 | [点击查看](https://gitcode.com/Ascend/mssanitizer) |
| **msDebug** | **【原生调试】** 基于昇腾处理器的原生环境调试，支持变量展示、单步调试及上板调试。 | [点击查看](https://gitcode.com/Ascend/msdebug) |
| **msOpProf** | **【性能分析】** 支持上板与仿真数据采集，通过 MindStudio Insight 可视化定位性能瓶颈。 | [点击查看](https://gitcode.com/Ascend/msopprof) |
| **msKL** | **【快捷调用】** 提供 Python 接口，快速实现 Kernel 的代码生成、编译及下发运行。 | [点击查看](https://gitcode.com/Ascend/mskl) |

## 快速入门
以开发一个简单的加法算子为例，贯穿算子开发全流程，10分钟快速体验msKPP(设计)、msOpGen(开发)、msSanitizer(检测)、msDebug(调试)、msOpProf(调优)工具的核心功能。    
详细操作指导请参见：[《算子开发工具链快速入门》](docs/zh/quick_start/op_tool_quick_start.md)。

## 安装指南
介绍msOT工具的环境依赖及安装方式，具体请参见[《msOT安装指南》](./docs/zh/install_guide/msot_install_guide.md)。

## 使用指南
各工具的详细使用指南请参阅其源码仓库中的 README 文件，源码仓库地址详见[功能介绍](#功能介绍)表中最后一列。

## 贡献指南
详细说明请参见[《msOT 贡献流程说明》](./docs/zh/common/contribute_workflow.md)。  

## License
详细说明请参见[《msOT License声明》](./docs/zh/common/license_notice.md)。  

## 免责声明
详细说明请参见[《msOT 免责声明》](./docs/zh/common/disclaimer.md)。  

## 建议与交流
欢迎大家为社区做贡献。如果有任何疑问或建议，请提交[Issues](https://gitcode.com/Ascend/msot/issues)，我们会尽快回复。感谢您的支持。

## 致谢
本工具由华为公司的下列部门贡献：   
- 计算产品线   

感谢来自社区的每一个PR，欢迎贡献。
