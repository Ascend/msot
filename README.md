<h1 align="center">MindStudio Operator Tools</h1>

<div align="center">
<p><b><span style="font-size: 24px;">昇腾 AI 算子开发工具链</span></b></p>

 [![快速入门](https://badgen.net/badge/快速入门/QuickStart/blue)](docs/zh/quick_start/op_tool_quick_start.md)
 [![AI问答(DeepWiki)](https://badgen.net/badge/AI问答/DeepWiki/blue)](https://deepwiki.com/mindstudio-docs/master) 
 [![AI问答(ZRead)](https://badgen.net/badge/AI问答/ZRead/blue)](https://zread.ai/mindstudio-docs/master)
 [![精确搜索](https://badgen.net/badge/精确搜索/ReadTheDocs/blue)](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest/) 
 [![昇腾社区](https://badgen.net/badge/昇腾社区/Community/blue)](https://www.hiascend.com/cn/developer/software/mindstudio) 
 [![报告问题](https://badgen.net/badge/报告问题/Issues/blue)](https://gitcode.com/Ascend/msot/issues) 

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

请通过上方表格链接进入对应源码仓库，参见 README 中的《使用指南》；若需按场景选择工具，请参见《[msOT 工具选型指南](./docs/zh/user_guide/msot_user_guide.md)》。

## 🌌 智能检索

为提升文档查阅效率，我们提供多种高效检索方式：  
🔹 [精确搜索（ReadTheDocs）](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest)：关键词全文检索，直达接口、参数与报错等信息。  
🔹 [AI 问答（DeepWiki）](https://deepwiki.com/mindstudio-docs/master)：自然语言问答，快速把握项目架构与模块关系。  
🔹 [AI 问答（ZRead）](https://zread.ai/mindstudio-docs/master)：中文问答体验更优，精准定位功能用法与细节。  

## 🛠️ 贡献指南

欢迎参与项目贡献，请参见《[贡献指南](./docs/zh/contributing/contributing_guide.md)》。

## ⚖️ 相关说明

🔹《[版本说明](./docs/zh/release_notes/release_notes.md)》   
🔹《[许可证声明](./docs/zh/legal/license_notice.md)》    
🔹《[安全声明](./docs/zh/legal/security_statement.md)》     
🔹《[免责声明](./docs/zh/legal/disclaimer.md)》     

## 🤝 建议与交流

欢迎大家为社区做贡献。如果有任何疑问或建议，请提交 [Issues](https://gitcode.com/Ascend/msot/issues)，我们会尽快回复。感谢您的支持。

|                                                                            即时互动（微信群）                                                                             |                                                                                  官方资讯（公众号）                                                                                   | 深度支持（助手/论坛）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="https://raw.gitcode.com/Ascend/docs/files/master/common/Writing_Template/figures/qr_code_wechat_work.png" width="120"><br><sub>*扫码加入技术交流群*</sub> | <img src="https://raw.gitcode.com/Ascend/docs/files/master/common/Writing_Template/figures/qr_code_wechat_official_account.png" width="120"><br><sub>*扫码关注官方公众号*</sub> | 扫码入群并关注公众号，直达 MindStudio 用户与开发者最快捷的交流平台：<br> **快速提问：** 与社区小伙伴即时探讨技术问题<br>**掌握动态：** 第一时间获取版本发布与功能更新通知<br> **经验共享：** 与广大开发者交流最佳实践与实战心得  <br> <br> **更多支持渠道**：👉 昇腾助手：[![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](https://gitcode.com/Ascend/msit/blob/master/docs/zh/figures/readme/xiaozhushou.png) 👉 昇腾论坛：[![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 致谢

msOT 由华为公司的下列部门联合贡献：    
🔹 昇腾计算MindStudio开发部  
🔹 昇腾计算生态使能部  
🔹 华为云昇腾云服务  
🔹 2012编译器实验室  
🔹 2012马尔科夫实验室  
感谢来自社区的每一个 PR，欢迎贡献 msOT！
