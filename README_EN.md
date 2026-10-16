<h1 align="center">MindStudio Operator Tools</h1>

<div align="center">
<p><b><span style="font-size: 24px;">Ascend AI Operator Development Toolchain</span></b></p>

 [![Quick Start](https://badgen.net/badge/Quick%20Start/QuickStart/blue)](docs/en/quick_start/op_tool_quick_start.md)
 [![AI Q&A (DeepWiki)](https://badgen.net/badge/AI%20Q%26A/DeepWiki/blue)](https://deepwiki.com/mindstudio-docs/26.2.0) 
 [![AI Q&A (ZRead)](https://badgen.net/badge/AI%20Q%26A/ZRead/blue)](https://zread.ai/mindstudio-docs/26.2.0) 
 [![Exact Search](https://badgen.net/badge/Exact%20Search/ReadTheDocs/blue)](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest/) 
 [![Ascend Community](https://badgen.net/badge/Ascend%20Community/Community/blue)](https://www.hiascend.com/en/developer/software/mindstudio) 
 [![Report Issues](https://badgen.net/badge/Report%20Issues/Issues/blue)](https://atomgit.com/Ascend/msot/issues) 

</div>

English | [简体中文](./README.md)

## ✨ Latest News

<span style="font-size:14px;">

🔹 **[Dec 31, 2025]**: MindStudio Operator Tools fully open-sourced

</span>

## ℹ️ Overview

MindStudio Operator Tools (msOT) is an operator development toolchain that focuses on key challenges in operator development. By providing capabilities such as operator design, development framework generation, functional debugging, anomaly detection, and multi-dimensional performance tuning, it reduces the complexity of operator development and improves the delivery efficiency of high-performance operators.

<img src="./docs/en/figures/readme/fullview.svg" width="1200"/>

## ⚙️ Feature Overview

The operator development toolchain provides the following series of tools:

| Category | Tool Name | Feature Overview                                                      |
|:--:| :--- |:----------------------------------------------------------|
| Design | [**msKPP**](https://atomgit.com/Ascend/mskpp) | **[Performance Prediction]** Supports inputting operator descriptions to predict the performance upper limit of an operator under a specific algorithm implementation.                    |
| Build | [**msOpGen**](https://atomgit.com/Ascend/msopgen) | **[Project Generation]** An operator development efficiency improvement tool that provides template project generation capabilities, simplifying project setup.                  |
| Verification | [**msKL**](https://atomgit.com/Ascend/mskl) | **[Quick Invocation]** Provides a Python interface to quickly launch and run Kernels, facilitating rapid functional verification.         |
| Detection | [**msSanitizer**](https://atomgit.com/Ascend/mssanitizer) | **[Anomaly Detection]** Provides memory, race condition, uninitialized access, and synchronization detection, supporting precise localization of memory issues in multi-core programs.             |
| Debugging | [**msDebug**](https://atomgit.com/Ascend/msdebug) | **[Native Debugging]** Native environment debugging based on Ascend processors, supporting variable inspection, single-step execution, and on-device debugging.               |
| Tuning | [**msOpProf**](https://atomgit.com/Ascend/msopprof) | **[Performance Analysis]** Supports on-device and simulation data collection, and locates performance bottlenecks through the MindStudio Insight visualization tool. |

## 🚀 Quick Start

Taking a simple addition operator as an example, this guide covers the entire operator development process. See [Operator Development Toolchain Quick Start](docs/en/quick_start/op_tool_quick_start.md).

## 📦 Installation Guide

msOT tools support three installation methods: online installation, offline installation, and source code installation. For details, see the [msOT Installation Guide](./docs/en/install_guide/msot_install_guide.md).

## 📘 User Guide

Use the links in the feature overview table to access the corresponding source code repositories and see the User Guide in their README files. To select a tool based on your scenario, see the [msOT Tool Selection Guide](./docs/en/user_guide/msot_user_guide.md).

## 🌌 Intelligent Search

To improve documentation retrieval efficiency, we provide multiple search methods:  
🔹 [Precise Search (ReadTheDocs)](https://mindstudio-operator-tools-docs.readthedocs.io/zh-cn/latest): Search the full text by keyword and go directly to information such as APIs, parameters, and error messages.  
🔹 [AI Q&A (DeepWiki)](https://deepwiki.com/mindstudio-docs/26.2.0): Ask questions in natural language to quickly understand the project architecture and relationships between modules.   
🔹 [AI Q&A (ZRead)](https://zread.ai/mindstudio-docs/26.2.0): Provides a better Chinese Q&A experience and accurately locates feature usage and details.   

## 🛠️ Contribution Guide

Welcome to participate in project contributions. Please refer to the [Contribution Guide](./docs/en/contributing/contributing_guide.md).

## ⚖️ Related Notes

🔹 [Release Notes](https://atomgit.com/Ascend/msot/releases)   
🔹 [License Notice](./docs/en/legal/license_notice.md)    
🔹 [Security Statement](./docs/en/legal/security_statement.md)     
🔹 [Disclaimer](./docs/en/legal/disclaimer.md)     

## 🤝 Suggestions and Communication

Everyone is welcome to contribute to the community. If you have any questions or suggestions, please submit an [Issue](https://atomgit.com/Ascend/msot/issues), and we will respond as soon as possible. Thank you for your support.

|                                                                            Real-Time Interaction (WeChat Group)                                                                             |                                                                                  Official Information (Official Account)                                                                                   | In-Depth Support (Assistant/Forum)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://raw.atomgit.com/Ascend/docs/files/master/common/Writing_Template/figures/qr_code_wechat_work.png" width="120"><br><sub>*Scan the QR code to join the technical discussion group*</sub> | <img src="https://raw.atomgit.com/Ascend/docs/files/master/common/Writing_Template/figures/qr_code_wechat_official_account.png" width="120"><br><sub>*Scan the QR code to follow the official account*</sub> | Scan the QR code to join the group and follow the official account for the fastest way to connect with MindStudio users and developers:<br> **Ask questions quickly:** Discuss technical issues with community members in real time.<br>**Stay up to date:** Receive notifications about version releases and feature updates as soon as they are available.<br> **Share experience:** Exchange best practices and hands-on experience with developers.  <br> <br> **More support channels**: 👉 Ascend Assistant: [![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](https://atomgit.com/Ascend/msit/blob/master/docs/zh/figures/readme/xiaozhushou.png) 👉 Ascend Forum: [![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 Acknowledgments

This tool is jointly contributed by Huawei Technologies Co., Ltd. and developers.

Thanks for every PR from the community, and contributions are welcome.
