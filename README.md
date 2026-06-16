<h1 align="center">MindStudio Operator Tools</h1>

<div align="center">
<h2>昇腾 AI 算子开发工具链</h2>

 [![Ascend](https://img.shields.io/badge/Community-MindStudio-blue.svg)](https://www.hiascend.com/developer/software/mindstudio) 
 [![License](https://badgen.net/badge/License/MulanPSL-2.0/blue)](./LICENSE)

</div>

## ✨ 最新消息

<span style="font-size:14px;">

🔹 **[2025.12.31]**：MindStudio 算子开发工具链全面开源

</span>

## ℹ️ 简介

MindStudio Operator Tools（msOT）算子开发工具链，聚焦算子开发中的关键挑战。通过提供算子设计、开发框架生成、功能调试、异常检测与多维性能调优等能力，降低算子开发复杂度，提升高性能算子的交付效率。

<img src="./docs/zh/figures/readme/fullview.svg?v=2026033001" width="1200"/>

## ⚙️ 功能介绍

算子开发工具链提供以下系列化工具：

| 类别 | 工具名称 | 功能简介                                                      |
|:--:| :--- |:----------------------------------------------------------|
| 设计 | [**msKPP**](https://gitcode.com/Ascend/mskpp) | **【性能预测】** 支持输入算子描述，预测算子在特定算法实现下的性能上限。                    |
| 构建 | [**msOpGen**](https://gitcode.com/Ascend/msopgen) | **【工程生成】** 算子开发效率提升工具，提供模板工程生成能力，简化工程搭建。                  |
| 验证 | [**msKL**](https://gitcode.com/Ascend/mskl) | **【快捷调用】** 提供 Python 接口，快速实现 Kernel 的下发运行，便于快速完成功能验证。         |
| 检测 | [**msSanitizer**](https://gitcode.com/Ascend/mssanitizer) | **【异常检测】** 提供内存、竞争、未初始化及同步检测，支持多核程序内存问题的精准定位。             |
| 调试 | [**msDebug**](https://gitcode.com/Ascend/msdebug) | **【原生调试】** 基于昇腾处理器的原生环境调试，支持变量查看、单步执行及上板调试。               |
| 调优 | [**msOpProf**](https://gitcode.com/Ascend/msopprof) | **【性能分析】** 支持上板与仿真数据采集，通过 MindStudio Insight 可视化工具定位性能瓶颈。 |

## 🚀 快速入门

以简易加法算子为例，完整贯穿算子开发全流程，请参见《[算子开发工具链快速入门](docs/zh/quick_start/op_tool_quick_start.md)》。

## 📦 安装指南

介绍 msOT 工具的环境依赖与安装方法，请参见《[msOT 安装指南](./docs/zh/install_guide/msot_install_guide.md)》。

## 📘 使用指南

请查阅《[msOT 使用指南](./docs/zh/user_guide/msot_user_guide.md)》，根据具体应用场景选用相应工具，详细使用说明请参见其源码仓库中的 README 文件。

## 🛠️ 贡献指南

欢迎参与项目贡献，请参见《[贡献指南](./docs/zh/contributing/contributing_guide.md)》。

## ⚖️ 相关说明

🔹《[版本说明](./docs/zh/release_notes/release_notes.md)》   
🔹《[许可证声明](./docs/zh/legal/license_notice.md)》    
🔹《[安全声明](./docs/zh/legal/security_statement.md)》     
🔹《[免责声明](./docs/zh/legal/disclaimer.md)》     

## 🤝 建议与交流

欢迎大家为社区做贡献。如果有任何疑问或建议，请提交 [Issues](https://gitcode.com/Ascend/msot/issues)，我们会尽快回复。感谢您的支持。

|                                      📱 关注 MindStudio 公众号                                       | 💬 更多交流与支持                                                                                                                                                                                                                                                                                                                                                                                                                     |
|:-----------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="./docs/zh/figures/readme/officialAccount.png" width="120"><br><sub>*扫码关注获取最新动态*</sub> | 💡 **加入微信交流群**：<br>关注公众号，回复“交流群”即可获取入群二维码。<br><br>🛠️ **其他渠道**：<br>👉 昇腾助手：[![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](docs/zh/figures/readme/xiaozhushou.png)<br>👉 昇腾论坛：[![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 致谢

msOT 由华为公司的下列部门联合贡献：    
🔹 昇腾计算MindStudio开发部  
🔹 昇腾计算生态使能部  
🔹 华为云昇腾云服务  
🔹 2012编译器实验室  
🔹 2012马尔科夫实验室  
感谢来自社区的每一个 PR，欢迎贡献 msOT！
