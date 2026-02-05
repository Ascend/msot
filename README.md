# MindStudio Operator Tools

# 最新消息
* [2025.12.30]：MindStudio Operator Tools项目首次上线 

# 简介
MindStudio Operator Tools（算子开发，msOT）用于打包MindStudio后端命令行工具，后端命令行工具包括msDebug、msKL、msKPP、msOpGen、msOpSt、msOpProf、msSanitizer等工具。

# 目录结构
针对该软件仓，整体目录设计思路如下：
```
MindStudio-Operator-Tools
|-- .gitmodules           # 管理依赖的module文件
|-- build.py                # 一键式构建脚本入口
|-- CMakeLists.txt          # cmake构建入口，只包含编译过程，不包含打包
|-- cmake
    |-- module              # 各子模块构建cmake工程集成入口
├── msopprof                # msopprof子仓代码目录
├── mssanitizer             # mssanitizer子仓代码目录
├── msopgen                 # msopgen及msopst子仓代码目录
├── mskpp                   # mskpp子仓代码目录
├── msdebug                 # msdebug子仓代码目录
├── mskl                    # mskl子仓代码目录
|-- package
   |-- conf                 # 打包配置文件目录
   |-- script               # 打包及部署脚本文件目录
|-- thirdparty              # 三方依赖子仓存放目录
```
---

# 环境部署
## 环境依赖
- 硬件环境请参见《[昇腾产品形态说明](https://www.hiascend.com/document/detail/zh/AscendFAQ/ProduTech/productform/hardwaredesc_0001.html)》。
- 工具的使用运行需要提前获取并安装CANN开源版本，当前CANN开源版本正在发布中，敬请期待。
## 工具安装
介绍msOT工具的环境依赖及安装方式，具体请参见[msOT安装指南](./docs/zh/msot_install_guide.md)。


# 快速入门
以开发一个简单的加法算子为例，贯穿算子开发全流程，10分钟快速体验msKPP(设计)、msOpGen(开发)、msSanitizer(检测)、msDebug(调试)、msOpProf(调优)工具的核心功能。详细操作指导请参见：[《快速入门》](docs/zh/quick_start/op_tool_quick_start.md)。

# 功能介绍
*   [msKPP（MindStudio Kernel Performance Prediction） ](https://www.hiascend.com/document/detail/zh/mindstudio/830/ODtools/Operatordevelopmenttools/atlasopdev_16_0006.html)   
支持用户输入算子表达，进而预测算子在这一算法实现下的性能上限。

*  [msKL（MindStudio Kernel Launcher）](https://www.hiascend.com/document/detail/zh/mindstudio/830/ODtools/Operatordevelopmenttools/atlasopdev_16_0173.html)    
使用msKL工具可以利用提供的接口在Python脚本中快速实现Kernel下发代码生成、编译及运行Kernel。

* [msOpGen（MindStudio Ops Generator ） ](https://www.hiascend.com/document/detail/zh/mindstudio/830/ODtools/Operatordevelopmenttools/atlasopdev_16_0018.html)  
包含msOpGen和msOpST（MindStudio Ops System Test）工具。msOpGen是算子开发效率提升工具，提供模板工程生成能力，简化算子工程搭建并辅助算子测试验证。msOpST是算子开发效率提升工具，旨在真实的硬件环境中，对算子的输入输出进行测试，以验证算子的功能是否正确。

*  [msSanitizer（MindStudio Sanitizer）](https://www.hiascend.com/document/detail/zh/mindstudio/830/ODtools/Operatordevelopmenttools/atlasopdev_16_0039.html)  
算子异常检测工具，提供内存检测、竞争检测、未初始化检测及同步检测的能力，支持多核程序下内存问题的精准定位。

* [msDebug（MindStudio Debugger）  ](https://www.hiascend.com/document/detail/zh/mindstudio/830/ODtools/Operatordevelopmenttools/atlasopdev_16_0062.html)  
提供基于昇腾处理器的原生环境调试能力，实现灵活的变量展示。支持算子功能调试，单步调试（上板）等功能。

*  [msOpProf（MindStudio Ops Profiler）](https://www.hiascend.com/document/detail/zh/mindstudio/830/ODtools/Operatordevelopmenttools/atlasopdev_16_0082.html)   
提供上板和仿真的性能数据采集方式，并通过MindStudio Insight进行可视化呈现，方便用户快速定位算子性能瓶颈。


# 免责声明
## 致msOT使用者
- 本工具仅供调试和开发之用，使用者需自行承担使用风险，并理解以下内容：
    - 数据处理及删除：用户在使用本工具过程中产生的数据属于用户责任范畴。建议用户在使用完毕后及时删除相关数据，以防信息泄露。
    - 数据保密与传播：使用者了解并同意不得将通过本工具产生的数据随意外发或传播。对于由此产生的信息泄露、数据泄露或其他不良后果，本工具及其开发者概不负责。
    - 用户输入安全性：用户需自行保证输入的命令行的安全性，并承担因输入不当而导致的任何安全风险或损失。对于由于输入命令行不当所导致的问题，本工具及其开发者概不负责。
- 免责声明范围：本免责声明适用于所有使用本工具的个人或实体。使用本工具即表示您同意并接受本声明的内容，并愿意承担因使用该功能而产生的风险和责任，如有异议请停止使用本工具。
- 在使用本工具之前，请谨慎阅读并理解以上免责声明的内容。对于使用本工具所产生的任何问题或疑问，请及时联系开发者。
## 致数据所有者
如果您不希望您的模型或数据集等信息在msOT中被提及，或希望更新msOT中有关的描述，请在Gitcode提交issue，我们将根据您的issue要求删除或更新您相关描述。衷心感谢您对msOT的理解和贡献。

# License

msOT产品的使用许可证，具体请参见[LICENSE](./LICENSE)文件。  
msOT工具docs目录下的文档适用CC-BY 4.0许可证，具体请参见[LICENSE](./docs/LICENSE)。


# 贡献声明
1. 提交错误报告：如果您在msOT中发现了一个不存在安全问题的漏洞，请在msOT仓库中的Issues中搜索，以防该漏洞已被提交，如果找不到漏洞可以创建一个新的Issues。如果发现了一个安全问题请不要将其公开，请参阅安全问题处理方式。提交错误报告时应该包含完整信息。
2. 安全问题处理：本项目中对安全问题处理的形式，请通过邮箱通知项目核心人员确认编辑。
3. 解决现有问题：通过查看仓库的Issues列表可以发现需要处理的问题信息, 可以尝试解决其中的某个问题。
4. 如何提出新功能：请使用Issues的Feature标签进行标记，我们会定期处理和确认开发。
5. 开始贡献：  
    1. Fork本项目的仓库。  
    2. Clone到本地。  
    3. 创建开发分支。  
    4. 本地测试：提交前请通过所有单元测试，包括新增的测试用例。  
    5. 提交代码。  
    6. 新建Pull Request。  
    7. 代码检视，您需要根据评审意见修改代码，并重新提交更新。此流程可能涉及多轮迭代。  
    8. 当您的PR获得足够数量的检视者批准后，Committer会进行最终审核。  
    9. 审核和测试通过后，CI会将您的PR合并入到项目的主干分支。

# 建议与交流

欢迎大家为社区做贡献。如果有任何疑问或建议，请提交[Issues](https://gitcode.com/Ascend/msot/issues)，我们会尽快回复。感谢您的支持。


#  致谢

msOT由华为公司的下列部门联合贡献：

- 计算产品线

感谢来自社区的每一个PR，欢迎贡献msOT。
