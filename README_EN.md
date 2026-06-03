<!-- md-trans-meta sourceCommit=unknown translatedAt=2026-05-20T02:05:13.007Z pushedAt=2026-05-20T08:00:02.361Z -->

<h1 align="center">MindStudio Operator Tools</h1>

<div align="center">
<h2>Ascend AI Operator Development Toolchain</h2>

 [![Ascend](https://img.shields.io/badge/Community-MindStudio-blue.svg)](https://www.hiascend.com/developer/software/mindstudio) 
 [![License](https://badgen.net/badge/License/MulanPSL-2.0/blue)](./LICENSE)

</div>

## ✨ Latest News

<span style="font-size:14px;">

🔹 **[2025.12.31]**: MindStudio Operator Tools fully open-sourced

</span>

## ℹ️ Overview

MindStudio Operator Tools (msOT) is an operator development toolchain that focuses on key challenges in operator development. By providing capabilities such as operator design, development framework generation, functional debugging, anomaly detection, and multi-dimensional performance tuning, it reduces the complexity of operator development and improves the delivery efficiency of high-performance operators.

<img src="./docs/en/figures/readme/fullview.svg?v=2026033001" width="1200"/>

## ⚙️ Feature Overview

The Operator Development toolchain provides the following series of tools:

| Category | Tool Name | Feature Overview                                                      |
|:--:| :--- |:----------------------------------------------------------|
| Design | [**msKPP**](https://gitcode.com/Ascend/mskpp) | **[Performance Prediction]** Supports inputting operator descriptions to predict the performance upper limit of an operator under a specific algorithm implementation.                    |
| Build | [**msOpGen**](https://gitcode.com/Ascend/msopgen) | **[Project Generation]** An operator development efficiency improvement tool that provides template project generation capabilities, simplifying project setup.                  |
| Verification | [**msKL**](https://gitcode.com/Ascend/mskl) | **[Quick Invocation]** Provides a Python interface to quickly launch and run Kernels, facilitating rapid functional verification.         |
| Detection | [**msSanitizer**](https://gitcode.com/Ascend/mssanitizer) | **[Anomaly Detection]** Provides memory, race condition, uninitialized access, and synchronization detection, supporting precise localization of memory issues in multi-core programs.             |
| Debugging | [**msDebug**](https://gitcode.com/Ascend/msdebug) | **[Native Debugging]** Native environment debugging based on Ascend processors, supporting variable inspection, single-step execution, and on-device debugging.               |
| Tuning | [**msOpProf**](https://gitcode.com/Ascend/msopprof) | **[Performance Analysis]** Supports on-device and simulation data collection, and locates performance bottlenecks through the MindStudio Insight visualization tool. |

## 🚀 Quick Start

Taking a simple addition operator as an example, which covers the entire operator development process, see [Operator Development Toolchain Quick Start](docs/en/quick_start/op_tool_quick_start.md).

## 📦 Installation Guide

For an introduction to the environment dependencies and installation methods of msOT tools, see [msOT Installation Guide](./docs/en/install_guide/msot_install_guide.md).

## 📘 User Guide

For detailed usage instructions of each tool, please refer to the README files in their respective source code repositories, or you can directly jump via the links in the feature overview table above.

## 🛠️ Contribution Guide

Welcome to participate in project contributions. Please refer to the [Contribution Guide](./docs/en/contributing/contributing_guide.md).

## ⚖️ Related Notes

🔹 [Release Notes](./docs/en/release_notes/release_notes.md)   
🔹 [License Notice](./docs/en/legal/license_notice.md)    
🔹 [Security Statement](./docs/en/legal/security_statement.md)     
🔹 [Disclaimer](./docs/en/legal/disclaimer.md)     

## 🤝 Suggestions and Communication

Everyone is welcome to contribute to the community. If you have any questions or suggestions, please submit an [Issue](https://gitcode.com/Ascend/msot/issues), and we will respond as soon as possible. Thank you for your support.

|                                      📱 Follow MindStudio Official Account                                       | 💬 More Communication and Support                                                                                                                                                                                                                                                                                                                                                                                                                     |
|:-----------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="./docs/zh/figures/readme/officialAccount.png" width="120"><br><sub>*Scan the QR code to get the latest updates*</sub> | 💡 **Join the WeChat Group**:<br>Follow the official account and reply "communication group" to get the group QR code.<br><br>🛠️ **Other Channels**:<br>👉 Ascend Assistant: [![WeChat](https://img.shields.io/badge/WeChat-07C160?style=flat-square&logo=wechat&logoColor=white)](docs/zh/figures/readme/xiaozhushou.png)<br>👉 Ascend Forum: [![Website](https://img.shields.io/badge/Website-%231e37ff?style=flat-square&logo=RSS&logoColor=white)](https://www.hiascend.com/forum/) |

## 🙏 Acknowledgments

msOT is jointly contributed by the following departments of Huawei:    
🔹 Ascend Computing MindStudio Development Department  
🔹 Ascend Computing Ecosystem Enablement Department  
🔹 Huawei Cloud Ascend Cloud Service  
🔹 2012 Compiler Lab  
🔹 2012 Markov Lab  
Thank you for every PR from the community, and welcome to contribute to msOT.
