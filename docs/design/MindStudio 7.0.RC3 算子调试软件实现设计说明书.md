# **MindStudio 7.0.RC3算子调试软件实现设计说明书**

修订记录

| **Date**   **日期** | **Revision Version**   **修订版本** | **Revision**   **Chapter**   **修订章节** | **Change Description**   **修改描述** | **Author**   **作者** |
| ------------------- | ----------------------------------- | ----------------------------------------- | ------------------------------------- | --------------------- |
| 2023-8-3            | 1.0                                 |                                           | 初稿完成                              | XXX                   |
| 2023-8-10           | 1.1                                 |                                           | 补充完善                              | XXX                   |
| 2023-11-06          | 1.2                                 |                                           | 补充修改                              | XXX                   |
| 2024-01-18          | 1.3                                 |                                           | 补充完善                              | XXX                   |
| 2024-06-15          | 1.4                                 |                                           | 补充完善                              | XXX                   |

 [TOC]

# 1    概述

## 1.1    目的

算子调试功能本身包含异常检测，功能调试，性能调优三大组件。现有工具中，功能调试工具仅有仿真调试能力。对于功能调试，现有的仿真调试存在仿真与真实结果不一致且性能差的问题。

针对 kernel 的调试调优，主要用户为昇腾算子开发人员，包括客户算子开发工程师和公司内部算子开发工程师。

本文目的是对算子调试功能进行设计，明确主要数据结构和主要处理过程，作为今后的编码阶段的输入和编码人员、测试人员的指导。

## 1.2    范围

1、 上板调试支持910B芯片、 310P芯片

# 2    模块简介（架构设计）

## 2.1    Ascend C支持上板单步调试模块

### 2.1.1    模块概述

#### i.      概述

由于异构芯片内部存在多核并发等情况，且为了追求极限性能，代码本身校验措施较少，且需要基于芯片架构充分发挥性能，纯粹的功能仿真无法满足调试要求，需要支持在真实芯片运行环境中，对算子代码进行调试。

#### ii.      模块上下文定义

![img](../pic/888b76f485ac928a30893faa11078a2f_598x250.jpg@900-0-90-f.jpg)

### 2.1.2    总体结构

![img](../pic/a7ac427427a0d41a2cb2c0fcbd522412_692x321.gif@900-0-90-f.gif)

​		Ascend C上板调试功能涉及调试器、编译器、驱动、RTS等多个周边组件，本调试模块msdebug属于调试器，部署于CANN架构元素中，配合编译器提供的调试信息，依赖runtime动态库，并使用ts_debug.ko提供的驱动接口向device侧的TSFW下发调试命令，或借助PCIe接口向device侧内存下发断点指令，TSFW接收到调试通知后触发对应的DEBUGGER_API启用调试功能，完成调试后向ts_debug.ko返回处理结果，并返回消息至msdebug，完成一次标准的上板单步调试命令流。通过对DEBUGGER_API的扩展，可分别实现断点设置、恢复运行、单步运行、内存读取、寄存器读取等业务功能，并支持对新功能的扩展。

### 2.1.3    设计约束

1、 lldb上板调试能力受限于Driver、RTS提供的能力，以及编译器能够提供的DWARF信息。

### 2.1.4    遵循标准

#### i.      技术限制

操作系统：Linux

编程语言：C++

#### ii.      模块规格

NA

#### iii.      设计思路

该模块主要基于lldb原代码进行修改，参照原有流程补充增加针对昇腾设备的实现。同时通过动态加载的方式引用昇腾设备的驱动接口，实现与设备进行交互。

# 3    模块需求分析

## 3.1    软件功能描述

1、 Ascend C支持上板单步调试。

2、 支持CANN软件。

## 3.2    关键场景分析

| **场景编号** | **场景描述**                               | **场景对应的需求** |
| ------------ | ------------------------------------------ | ------------------ |
| 1            | lldb支持断点设置                           | XXX                |
| 2            | lldb支持感知进程运行状态                   | XXX                |
| 3            | lldb支持变量地址获取与打印                 | XXX                |
| 4            | lldb支持用户进行核间内存选择               | XXX                |
| 5            | lldb状态信息展示                           | XXX                |
| 6            | 在板调试支持寄存器读                       | XXX                |
| 7            | 在板调试支持单核step命令                   | XXX                |
| 8            | 在板调试支持中断特性                       | XXX                |
| 9            | 调试器支持多kernel下发场景下的特定算子调试 | XXX                |
| 10           | 支持可视化调试能力                         | XXX                |

### 3.2.1    Ascend C支持上板单步调试模块关键场景分析

#### i.      lldb支持断点设置

介绍

lldb需要支持对Ascend C算子程序进行断点设置，程序在命中断点时可以停止运行。

输入

​       用户使用b命令设置断点的位置信息。

输出

​       断点设置结果。

处理

![img](../pic/d01f4436ba919d5ab8e91a5e694f2ca5_545x362.jpg@900-0-90-f.jpg)

衍生场景 

​           lldb支持断点取消

​           lldb支持断点信息展示

#### ii.      lldb支持感知进程运行状态

介绍

lldb需要支持感知程序状态，在开始运行、命中断点等事件发生时能够及时响应。

输入

​       SQCQ通道上报的程序事件

输出

​       用户侧响应，展示程序状态信息

处理   

![img](../pic/ec131a9d7d63559747091f0efb60c698_494x328.jpg@900-0-90-f.jpg)

衍生场景

​           支持进程状态控制 

#### iii.      lldb支持变量地址获取与打印

介绍

lldb需要能够读取到变量的地址，以及打印地址上的值。

输入

​       用户调用p、x命令打印变量内容与地址值

输出

​       按照变量类型显示的变量值。

处理

![img](../pic/a6b465eab90af3a4f01c62c43d6b2d22_443x327.jpg@900-0-90-f.jpg)

衍生场景 

​           表达式的打印

#### iv.      lldb支持用户进行核间内存选择

介绍

lldb需要支持用户能够在核间进行切换，从而展示不同核上的运行情况。

输入

​       用户调用命令行ascend {aic,aiv} [id]

输出

​       切换结果。

处理

![img](../pic/cad607cfe8540eda776847142cd2cd5a_546x401.jpg@900-0-90-f.jpg)

衍生场景 

​           支持不同核间信息打印

#### v.      lldb支持用户展示信息

介绍

lldb需要支持用户能够展示core/task/stream/block相关的信息

输入

​       用户调用命令行ascend info cores/task/stream/block

输出

​       打印相关信息。

处理

![img](../pic/c55e294abf8a6b0ec47d7cb01055a8b7_692x437.gif@900-0-90-f.gif)

 

#### vi.      msdebug[支持读昇腾芯片寄存器](javascript:void(0))

介绍

 msdebug支持通用寄存器和特殊寄存器的信息读取。支持SU和VEC下的SRP和REG类型的Entity。

输入

​       用户调用命令行register _read GPR30/SYS_CNT --ascend等

输出

​       寄存器相关的值

处理

![img](../pic/a45332589f4ff1d1514044712a36ac55_651x420.gif@900-0-90-f.gif)

#### vii.      msdebug[支持step over调试](javascript:void(0))

介绍

 msdebug支持代码行按行步进调试。

输入

​       当算子程序断点在device侧代码后，用户命令行按  step over

输出

​       算子程序按代码行执行下去，停在下一代码行的位置

处理

![img](../pic/0bc944d0b09ce63de607d0d29135575f_693x503.gif@900-0-90-f.gif)

 

#### viii.      msdebug[支持ctrl-c](javascript:void(0))中断device

介绍

 msdebug支持ctrl-c中断device程序。

输入

​       当算子程序在跑device部分代码时，用户命令行按ctrl-c

输出

​       算子程序中断，显示device中断的代码行位置

处理

![img](../pic/a42f1a2ca3479e0751a62e2b59178112_683x493.gif@900-0-90-f.gif)

 

#### ix.      msdebug支持选择特定kernel调试

介绍

 msdebug支持在多kernel下发场景中选择特定kernel调试。这个需求场景的意义：当用户使用PyTorch API对单算子进行验证时，准备tensor数据或其他数据预处理工作中，可能会调用一些触发其他基础算子的PyTorch API，于是这样的单算子调用场景实际上是一个隐式的多算子调用场景，为使调试功能正确使能，在用户对期望调试的算子kernel代码设置断点后，调试器需要感知各算子kernel下发运行的时机并在正确的时机使能用户期望调试的算子，最终使程序停在用户期望的算子断点上。

输入

​       多算子kernel下发场景，用户在期望调试的算子代码中设置断点。

输出

​       算子程序在仅运行至用户选定的kernel时，使能调试功能，完成断点下发。

处理

在多算子kernel下发场景中，调试器需要满足如下的能力：

1)    明确用户期望调试的算子kernel，

2)    感知各算子kernel下发至device的时机，

3)    定义用户指定算子kernel与实际下发的算子kernel匹配方法，

4)    定义使能算子kernel调试的时机。

首先需要明确并获取用户期望调试的算子kernel object，在用户指定断点并成功匹配时，可获取被匹配的算子kernel object数据；其次通过劫持算子kernel下发的runtime接口，可感知到算子实际下发至device的时机；在对比用户指定的算子kernel与实际下发的算子kernel是否匹配时，可对算子的kernel object数据使用hash算法，通过比对两方生成的hash值是否一致来判断是否为同一个算子kernel；最后在匹配后，完成断点下发来使能调试。

![img](../pic/3e169f784069bccaa2c16cb5a3a83318_692x563.jpg@900-0-90-f.jpg)

用户场景如下所示：

![文本框: $ msdebug python3 call_add.py (msdebug) b add_custom.cpp:55   …… ① … (msdebug) run ... -> 55  	        outQueueZ.EnQue<half>(zLocal);     …… ② … (msdebug) ](../pic/5ef5f6ca22a0d5cac93bc6b5b2bd51e4_698x281.gif@900-0-90-f.gif)

①  ：用户设置对期望使能调试的算子kernel代码，设置了断点；

②  ：调试器跳过了其他算子kernel，在运行至设置断点的算子kernel时使能调试并命中了断点。

#### x.      msdebug支持可视化调试

介绍

 msdebug支持在IDE中对算子程序进行可视化调试。这个需求场景的意义：一般算子开发是在IDE中进行，而为了更流畅地对接算子在板调试能力，并降低调试器较复杂的命令行命令导致的高使用门槛，需要调试器与IDE插件协同实现功能的交互，在IDE中向用户提供图形化的在板调试能力。

输入

用户在IDE中通过插件，在图形化界面上对算子程序进行断点设置、程序暂停、恢复、单步运行、变量读取、内存读取、寄存器展示、切核等调试行为， IDE插件将这些调试行为转化为具体的调试命令文本发送至调试器机机接口，并实际下发至调试器内部。

输出

调试器响应调试命令，完成程序控制等行为后，通过机机接口向IDE插件返回结构化的文本信息，在IDE插件解析后在IDE界面反馈并图形化展现。反馈包括：命中断点后高亮断点所在代码行，变量栏展示所有局部变量的值，监视栏展示监视的变量的值，弹出查询的内存与寄存器信息，状态栏显示所在核信息，切核后弹出核所在代码行信息等。

处理

调试器提供一个机器友好的调试交互接口lldb-mi，使调试器以统一的协议格式对接不同IDE框架（比如VSCode、MindStudio）的调试器插件，插件解析文本数据，并转化为图形界面反馈给用户。为兼容各类IDE的调试器插件，抽象一个机机接口的代理模块向插件提供交互接口，接口协议格式相比原本的命令行输出更加的结构化，易于被机器所解析。

![img](../pic/246f7ced29c61c57334c92053fe3397a_348x494.gif@900-0-90-f.gif)

![img](../pic/2f779ad4738bbbb705556a7b5c0de1c0_692x456.jpg@900-0-90-f.jpg)

# 4    模块概要设计

## 4.1    Ascend C支持上板单步调试模块概要设计

### 4.1.1    模块总体描述

本模块主要分为以下五个子模块，如下图所示：

![img](../pic/8420ed0959571e49fdcc1eed7972a120_692x460.jpg@900-0-90-f.jpg)

其中命令行模块多为lldb原实现，在本文中不做赘述。

### 4.1.2    模块分解描述

#### i.      设备交互模块

**目的**：该模块主要用于实现lldb-server和设备的交互功能，为其他模块提供与设备交互的接口。

**功能列表**：

1)        支持与设备建立交互通道

2)        支持通过交互通道向设备发送消息

3)        支持通过交互通道接收设备发送的消息

4)        支持维护用户当前访问的设备信息上下文

**处理**：该模块主要利用驱动提供的调试通道与GM内存访问接口，实现与设备进行消息交互，以及芯片上内存的读取。该模块包含以下5个部分，均封装在DeviceContext对象中：

1)        与设备通过调试通道建立连接

2)        通过驱动提供的GM内存访问接口，对其余模块提供GM内存读写的能力

3)        通过ioctl发送接口，对其余模块提供向RTS侧发送消息的能力，来支持对片上内存的读写，寄存器读写等操作。

4)        通过ioctl接收接口，创建消息接收线程，并将接收到的消息分发到其余模块

5)        维护用户当前访问的设备信息上下文，例如当前所处的CoreId等信息。

![img](../pic/519b977b055cd7e3c314ada0f3ea8a8a_632x347.jpg@900-0-90-f.jpg)

连接建立时序图：

![img](../pic/1d2c7c577388410f871e9dcac3a0bc35_691x493.gif@900-0-90-f.gif)

#### ii.      断点管理模块

**目的**：该模块主要用于支持用户通过lldb-client来完成断点设置、断点查看、断点取消等操作。

**功能列表**：

1)        支持设置断点

2)        支持取消断点

3)        支持查看断点

4)        支持断点失效/重新生效

**处理**：该模块主要用于借助设备交互模块提供的GM内存修改能力，通过断点信息修改对应pc地址上的指令，并通过RTS接口刷新指令cache使能断点生效。

​    硬断点设置：

![img](../pic/b867dc65e54644e77f08c6fdd3d49051_692x315.jpg@900-0-90-f.jpg)

​    软断点设置：

![img](../pic/5a38ad38f5778b86a169b3ff249c82d1_693x555.jpg@900-0-90-f.jpg)

#### iii.      进程控制模块

**目的**：该模块主要用于控制程序的运行，以及感知程序的状态变化

**功能列表**：

1)        支持感知程序状态变化

2)        支持控制程序状态（主要是控制程序继续运行）

**处理**：该模块主要是接收处理从设备交互模块接收到的进程状态变更，并在client侧做出响应。同时也要支持通过设备交互模块来控制进程状态（主要是continue）。

![img](../pic/d31deb3d96bd3496051abb7d4fcde0e1_692x562.jpg@900-0-90-f.jpg)

#### iv.      变量读写模块

**目的**：该模块主要用于给用户提供变量读写的能力。当用户进程停住时，用户可以打印，修改断点处可以访问到的代码中的变量。当前仅计划支持读取。

**功能列表**：

1)        支持打印变量

2)        支持打印简单表达式

**处理**：该模块主要通过从DWARF信息中获取变量的类型和偏移地址，然后通过得到的地址去设备交互模块查询对应的内存数据。

![img](../pic/3f62e98aa1d832ec67cea7710b2a4017_692x505.gif@900-0-90-f.gif)

#### v.      信息展示模块

**目的**：该模块主要用于给用户提供程序中断时，不同aicore的代码运行情况展示。

**功能列表**：

1)        支持根据cores/tasks/streams/blocks维度打印变量

2)        支持切换不同aicore显示代码运行位置的展示，不同aicore的状态，如step over/ breakpoint / signal / trace。

**处理**：该模块主要通过设备交互模块，获取每个aicore此时的pc地址等信息，然后匹配对应的代码行以及终端原因 

![img](../pic/ce4a403eb823c122dd376f65367b55e6_689x325.gif@900-0-90-f.gif)

#### vi.      调试使能模块

**目的**：该模块支持使能算子调试功能，包括获取算子kernel中包含的调试DWARF信息与算子核函数断点使能所需的运行时信息，并在不同算子拉起方式下支持使能调试功能，在多个kernel算子拉起时支持针对特定的kernel使能调试功能。。

**功能列表**：

1)        支持多种算子拉起场景下获取算子kernel object二进制段与运行时信息，场景包括使用算子运算符（<<<>>>）调用算子、使用aclnn流程调用算子、使用PyTorch API进行以上流程完成算子调用；

2)        支持多kernel算子拉起时，针对指定kernel使能断点配置并命中断点进入调试交互界面；

**处理**：该模块主要通过从不同文件中获取算子的kernel object二进制段，然后解析为lldb里的Module对象，用于后续断点设置与变量解析等调试功能。同时该模块还通过对比获取的算子kernel object二进制段与当前运行的算子kernel object二进制段是否一致，来调整调试功能的使能时机。

kernel object二进制段获取均在调试器完成，针对不同的场景，调试器可在加载程序时获取

![img](../pic/c215c5169b41f8624e8f816ae9e07034_692x347.gif@900-0-90-f.gif)

算子运行时信息获取：

![img](../pic/559c3c36251ad88b5f4c78185853cc7f_692x643.jpg@900-0-90-f.jpg)

特定算子使能：

![img](../pic/d80fa57cc2753803677b8d41001e01cd_692x562.jpg@900-0-90-f.jpg)

#### vii.      机机接口模块

**目的**：该模块向IDE调试器插件提供机器友好的调试交互接口，使调试器以统一的协议格式对接不同IDE框架的调试器插件。该模块一方面接收外部客户端插件发送来的调试命令，指示调试器执行特定操作，比如设置断点；另一方面，该模块在处理完调试命令后，以结构化的文本格式向外部客户端传输程序状态、变量等调试相关信息。

**功能列表**：

1)        支持接收外部输入的调试命令并解析执行；

2)        支持构造结构化的文本信息向外部返回调试结果；

**处理**：该模块（LLDB-MI DRIVER）可等价替代命令行客户端LLDB Command line，从外部接收调试命令，向调试器server发出调试命令，与原命令行客户端不同的是，原本按照人类友好格式输出的调试结果，比如断点、变量信息会按照特定的结构化文本信息流返回外部，易于供外部机器解析。

![img](../pic/886fc42d8ff3c684eda6530f91d0fbf3_693x302.gif@900-0-90-f.gif)

### 4.1.3    数据实体描述

 NA

### 4.1.4    依赖性描述

#### i.      运行设计

![lldb-rts_api](../pic/01cacfc6bdfbbb3ce89d5d221cba8efd_692x582.jpg@900-0-90-f.jpg)

图 ‑3 调试器实现断点/打印功能时序图

过程说明：

1：拉起用户进程，在子进程中设置LD_PRELOAD，使能桩函数，并阻塞（原机制）子进程

2：用户在LLDB中设置断点，并保存信息（此时未真正下发断点到设备）

3： LLDB通知用户程序运行（原机制）

4：当用户运行到set device时，通过接口的劫持，使得device Id上报到了LLDB

5：LLDB通过ioctl让驱动通过调试通道给TS下发set debug，使得TS开启debug模式

6：桩文件通过runtime拿到start pc

7：LLDB通过ioctl让驱动修改GM指令内存，实现软断点的设置

8：LLDB通知runtime继续执行

9：TS通过SQCQ上报**断点命中信息**，并停止对应核的指令调度

10：LLDB此时根据用户打印变量的命令，通过ioctl让驱动通过调试通道获取寄存器读取，内存读取的消息

11：LLDB此时根据用户打印变量的命令，通过ioctl让驱动通过调试通道，获取算子任务涉及的task_id, stream_id, core数量等信息。

12：LLDB将原断点指令恢复

13：LLDB通过SQCQ通知TS进行single step

14：LLDB通过驱动接口重新覆写软断点

#### ii.      数据依赖关系

NA

### 4.1.5    接口描述

#### i.      对外接口描述

| 接口                                                        | 描述                                                       | 交互对象 | 调用方 |
| ----------------------------------------------------------- | ---------------------------------------------------------- | -------- | ---- |
| lldb                                                        | Ascend C使用lldb调试调用对象                                | 用户     | 1    |
| lldb-mi                                                     | 使用机机接口调试调用对象                                   | 用户     | 1    |
| breakpoint命令                                              | 用户用于设置断点的命令                                     | 用户     | 1    |
| print命令                                                   | 用户用于打印变量的命令                                     | 用户     | 1    |
| memory read命令                                             | 用于打印地址信息的命令                                     | 用户     | 1    |
| ascend {aiv,aic} [id]                                       | 用于指定用户当前需要访问的核的命令                         | 用户     | 1    |
| ascend info {aicores,devices,tasks,streams, blocks,threads} | 用于展示当前的设备、核信息、stream/task/blocks/codes的命令 | 用户     | 1    |
| continue                                                    | 用于使停住的进程继续运行的命令                             | 用户     | 1    |
| run                                                         | 用于运行加载的二进制的命令                                 | 用户     | 1    |
| file                                                        | 用于加载二进制的命令                                       | 用户     | 1    |
| step over                                                   | 指定源码级单步命令                                         | 用户     | 1    |
| ascend set -mode                                            | 指定单核、多核模式调试                                     | 用户     | 1    |
| ctrl-c                                                      | 用于终止当前算子程序，展示device中断位置                   | 用户     | 1    |
| image add                                                   | 导入算子调试信息，同时指定需调试的算子kernel               | 用户     | 1    |
| image load                                                  | 加载指定module到内存指定地址                               | 用户     | 1    |
| export LAUNCH_KERNEL_PATH                                   | 导入算子调试信息，同时指定需调试的算子kernel               | 用户     | 1    |
| "*stopped,reason=\"device-breakpoint-hit\"                  | 机机接口对外输出该文本，用于标识已命中核函数断点           | 用户     | 0    |

#### ii.      内部接口描述

设备交互模块：

| 接口                                                         | 描述                                                         | 返回值                    | 交互对象                   | 调用方 |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------- | -------------------------- | ---- |
| DeviceContext::ReadMemory(lldb::addr_t addr, size_t size, const  MemoryTypeInfo &memory_type_info, void *out) | 设备交互模块对外部提供的读内存接口                           | 返回带有error信息的Status | 断点管理模块、变量读写模块 | 2    |
| DeviceContext::WriteGlobalMemory(addr_t addr, size_t size, const void  *data) | 设备交互模块对外部提供的写内存接口，当前主要用于设置断点、恢复断点 | 返回带有error信息的Status | 断点管理模块、进程控制模块 | 2    |
| DeviceContext::ReadRegister(uint32_t reg_num, uint32_t core_id,  CoreType core_type, uint64_t &value) | 设备交互模块对外部提供的读寄存器接口                         | Bool返回值，读取是否成功  | 变量读写模块               | 1    |
| DeviceContext::SetBreakpointCallback(const Callback &callback) | 设备交互模块对外部提供注册进程状态变化回调接口               | Void                      | 进程控制模块               | 1    |
| DeviceContext::Resume(uint64_t core_mask, uint8_t core_type) | 设备交互模块对外部提供的进程继续运行接口                     | 返回带有error信息的Status | 进程控制模块               | 1    |
| DeviceContext::SingleStep(uint64_t mask, CoreType core_type) | 设备交互模块对外提供的用于单步运行程序的命令                 | 返回带有error信息的Status | 进程控制模块               | 1    |
| DeviceContext::InvalidInstrCache(const addr_t &addr, uint8_t  redirect_ifu) | 设备交互模块对外提供的用于刷新指令缓存的接口                 | 返回带有error信息的Status | 断点管理模块               | 1    |
| DeviceContext::ReadGlobalMemory(addr_t addr, size_t size, void *data) | 设备交互模块对外部提供的读内存接口, 通过驱动直接dma读gm而不是ts接口 | 返回读取到的字节大小      | 断点管理模块               | 1    |
| DeviceContext::PauseTask()                                   | 设备交互模块对外提供的用于停止device程序的中断               | 返回是否下发成功          | 断点管理模块               | 1    |

变量读写模块:

| 接口                                                         | 描述                                 | 返回值                    | 交互对象   | 调用方 |
| ------------------------------------------------------------ | ------------------------------------ | ------------------------- | ---------- | ---- |
| ProcessGDBRemote::DoReadDeviceRegister(int regId, RegisterType  register_type) | 新增的用于读指定device侧寄存器的接口 | 返回带有error信息的Status | 命令行模块 | 1    |
| ProcessGDBRemote::DoReadMemory(addr_t addr, void *buf, size_t size,  const ArchSpec &arch_spec, DeviceAddressClass address_class, Status &error) | 用于读取内存值的接口                 | 返回带有error信息的Status | 命令行模块 | 1    |

断点管理模块:

| 接口                                                         | 描述                 | 返回值                    | 交互对象                 | 调用方 |
| ------------------------------------------------------------ | -------------------- | ------------------------- | ------------------------ | ---- |
| NativeProcessLinux::SetBreakpoint(lldb::addr_t addr, uint32_t size,  bool hardware) | 用于设置断点的接口   | 返回带有error信息的Status | 命令行模块               | 1    |
| NativeProcessProtocol::EnableSoftwareBreakpoint(lldb::addr_t addr,  uint32_t size_hint) | 用于使能断点的接口   | 返回带有error信息的Status | 命令行模块、进程控制模块 | 2    |
| NativeProcessLinux::RemoveBreakpoint(lldb::addr_t addr, bool hardware) | 用于去使能断点的接口 | 返回带有error信息的Status | 命令行模块、进程控制模块 | 2    |

进程控制模块:

| 接口                                      | 描述                                           | 返回值                                 | 交互对象     | 调用方 |
| ----------------------------------------- | ---------------------------------------------- | -------------------------------------- | ------------ | ---- |
| NativeProcessLinux::Resume                | 用于继续运行程序的接口                         | 返回带有error信息的Status              | 命令行模块   | 1    |
| NativeProcessLinux::LaunchProcess         | 用于拉起二进制进程的接口                       | 返回带有error信息的Status              | 命令行模块   | 1    |
| AscendProcessLinux ::SetStoppedBySignal() | 停止device程序                                 | 返回带有error信息的status              | 命令行模块   | 1    |
| 环境变量$COMM_FD                          | 用于从调试使能模块接收算子运行时信息的pipe句柄 | 参考linux 标准read()/write()接口返回值 | 调试使能模块 | 1    |

调试使能模块：

| 接口             | 描述                                           | 返回值                                 | 交互对象     | 调用方 |
| ---------------- | ---------------------------------------------- | -------------------------------------- | ------------ | ---- |
| 环境变量$COMM_FD | 用于向进程控制模块发送算子运行时信息的pipe句柄 | 参考linux 标准read()/write()接口返回值 | 设备交互模块 | 1    |

### 4.1.6    UI设计（可选，前台服务涉及）

NA

### 4.1.7    错误处理

触发错误后按照如下原则进行处理：

1)    当错误不影响算子调试使能时，如未查询到用户指定的断点，仅打印日志提示用户；

2)    当错误导致算子调试功能无法使能时，如打开驱动失败、运行时信息获取失败、断点下发失败等，抛出异常终止调试，并提示用户功能异常；

3)    其他lldb原错误沿用原错误处理流程。

### 4.1.8    系统错误

在算子拉起时，会检查系统运行环境是否满足调试器正常运行，若不满足，由算子进程主动抛出异常，并由lldb捕获并在交互界面展示，同时终止调试过程，并提示错误码。

### 4.1.9    接口错误

| 接口                                                    | 异常描述                                   | 返回结果               |
| ------------------------------------------------------- | ------------------------------------------ | ---------------------- |
| Breakpoint命令                                          | 异常场景均和原lldb保持一致               | NA                     |
| Print命令                                               | 异常场景均和原lldb保持一致               | NA                     |
| Memory read命令                                         | Memory_type参数配置了无效值                | Invalid memory type    |
| Ascend {aiv,aic} [id]                                   | 未指定正确的核类型                         | Invalid core type      |
| 选择了未停止的核                                        | Select core is not stopped. Switch failed. | NA                      |
| 无效的核id                                              | Invalid core id                            | NA                       |
| Ascend info {aicores,devices,cores,blocks,streams,task} | 选择了无效的信息类型                       | Invalid info type      |
| 信息获取失败                                            | Get info failed.Reason:{具体的返回信息}    | NA                       |
| Continue                                                | 异常场景均和原lldb保持一致               | NA                     |
| Run                                                     | 连接建立失败                               | Connect device failed. |
| File                                                    | 异常场景均和原lldb保持一致               | NA                     |
| step over                                               | 异常场景均和原lldb保持一致               | NA                     |
| ascend set                                              | 异常场景均和原lldb保持一致               | NA                     |
| ctrl-c                                                  | 异常场景均和原lldb保持一致               | NA                     |
| image add                                               | 异常场景均和原lldb保持一致               | NA                     |
| image load                                              | 异常场景均和原lldb保持一致               | NA                     |

内部接口的异常返回请参照内部接口描述。

### 4.1.10  文件和目录结构描述

文件目录如下所示，msdebug由bin与lib目录组成，bin目录放置可执行文件与入口脚本，lib目录放置动态库提供所需功能。

![文本框: ├── msdebug │   ├── bin │   │   ├── lldb-mi │   │   ├── lldb-server │   │   ├── msdebug │   │   └── msdebug.bin │   └── lib │       ├── libedit.so.0 │       ├── liblldb.so.15 │       ├── libncurses.so.5 │       ├── libpanel.so.5 │       ├── libruntime_stub.so │       └── libtinfo.so.5 ](../pic/eff3ea4ab9b6129954103f266f406db5_485x490.gif@900-0-90-f.gif)

| 文件名             | 描述                               |
| ------------------ | ---------------------------------- |
| lldb-mi            | 调试机机接口                       |
| lldb-server        | 调试器服务端，用于程序控制         |
| msdebug            | 调试入口脚本，用于配置调试环境变量 |
| msdebug.bin        | 调试器人机接口                     |
| libedit.so.0       | 用于命令行快捷操作                 |
| liblldb.so.15      | 调试器功能库                       |
| libncurses.so.5    | 用于命令行快捷操作                 |
| libpanel.so.5      | 用于命令行快捷操作                 |
| libruntime_stub.so | runtime桩函数库，用于调试使能      |
| libtinfo.so.5      | 用于命令行快捷操作                 |

# 5    模块详细设计

## 5.1    Ascend C支持上板单步调试模块——设备交互模块接口设计

### 5.1.1    接口定义描述

![img](../pic/97e365ed95b116c44ff08e1e19623939_689x959.jpg@900-0-90-f.jpg)

AscendProcessLinux会作为NativeProcessLinux的子类在lldb-server中提供服务，设备交互模块则主要集中在该类的成员变量m_device_context中。DeviceContext类会按设备操作的粒度向上层提供接口，下层则调用ioctl函数，传入DebugInfo结构体，根据ioctl第二个参数，决定是发送还是接收命令，结构体在驱动侧会做第一层解析，再通过调试通道下发命令到TS。 

### 5.1.2    处理流程描述

![img](../pic/b061f7251c5185a1225658dd6f3f699a_692x526.gif@900-0-90-f.gif)

### 5.1.3    关键函数描述

1、 DeviceContext::StartListenThread

该接口会启动一个监测线程，轮询TS的消息，监测的实现基于接口ioctl，命令字CMD_CQ_RECV 。接收到消息后，消息如果有对应的callback函数，则进行callback。轮询的动作，只有在不会发生ioctl CMD_SQ_SEND的场景下才会执行。每次要执行ioctl CMD_SQ_SEND操作时 ，需要先关闭轮询动作。

| **函数原型** | bool_t DeviceContext::StartListenThread  ()                  |
| ------------ | ------------------------------------------------------------ |
| **函数功能** | 用于启动监测线程，轮询ts的消息，根据消息进行不同的函数处理。 |
| **输入说明** | 无输入                                                       |
| **输出说明** | 启动成功返回true                                             |
| **注意事项** | 同一进程只能启动一次。                                       |

2、 DeviceContext::BaseSqCqComm

该接口是做一次基本的sq/cq，基于ioctl命令实现。

| **函数原型** | Status DeviceContext:: BaseSqCqComm(CmdType  type, const uint8_t *data = nullptr, const uint8_t len = 0, uint8_t *out =  nullptr, uint8_t out_len = 0); |
| ------------ | ------------------------------------------------------------ |
| **函数功能** | 做一次基本的sq/cq，基于ioctl命令实现，完成对ts一个命令的下发与接收返回结果。 |
| **输入说明** | type：发送接口的命令字  data: 每个命令字，对应的参数  len: 发送数据data的长度  out: 每个命令字对应的返回结果  out_len: 接收数据out的长度 |
| **输出说明** | 发送失败需要返回对应的错误信息                               |
| **注意事项** | 无                                                           |

3、 DeviceContext::ReadGlobalMemory

该接口用于读取GM内存，另外有对应的写GM内存的接口，该接口被用于设置软断点。

| **函数原型** | size_t DeviceContext::ReadGlobalMemory(addr_t  addr, size_t size, void *data); |
| ------------ | ------------------------------------------------------------ |
| **函数功能** | 接口用于读取GM内存，另外有对应的写GM内存的接口，该接口被用于设置软断点。该函数基于ioctl  CMD_GM_COPY命令字实现，和普通命令的区别是，不走TS逻辑，走驱动提供的DMA通道修改GM |
| **输入说明** | addr：device上的地址，绝对的虚拟地址  size: 要读取的字节数  data: 保存到host的地址 |
| **输出说明** | 发送失败需要返回对应的错误信息                               |
| **注意事项** | 无                                                           |

### 5.1.4    数据描述

不同的Send命令字，有对应不同的结构体

### 5.1.5    错误处理

| 错误场景           | 处理方案                                                     |
| ------------------ | ------------------------------------------------------------ |
| 打开设备侧失败     | 会在用户界面报错 “open driver fd failed, maybe device is already occupied by another  msdebug program.” |
| 设备侧KO没有插入     | 用户界面报错“Please insert debugger ko  before debugging.”   |
| 消息发送失败       | 开启DebugMode失败，会在用户界面返回失败“initialize debug mode failed, maybe ko/driver has problem.”。之后的消息发送失败则在日志里记录。 |
| 接收到请求失败响应 | 开启DebugMode失败，会在用户界面返回失败。之后的消息发送失败则在日志里记录。 |
| 消息接收超时       | 开启DebugMode失败，会在用户界面返回失败。之后的消息发送失败则在日志里记录。 |

### 5.1.6    测试设计

1、 正常路径

该模块正常路径下没有对用户侧的接口，可以通过其余模块的功能是否正常来完成

2、 异常路径

| 测试场景                               | 测试方案                                                     | 预期结果         |
| -------------------------------------- | ------------------------------------------------------------ | ---------------- |
| Debug模式在正常退出场景下是否正确关闭  | 运行调试程序正常结束后，再普通在同一设备上非调试场景下拉起一次算子进程，观察是否会卡住 | 算子进程正常运行 |
| Debug模式在异常退出场景下是否正确关闭  | 运行调试程序到一半后kill，再普通在同一设备上非调试场景下拉起一次算子进程，观察是否会卡住 | 算子进程正常运行 |
| 多个调试器用同一个Device调试，是否报错 | 运行调试程序1，设置断点，运行到停下来后；运行调试程序2，直接运行，观察是否报错 | 用户界面报错     |
| 不插KO，是否报错                       | 运行调试程序                                                 | 报错，提示先插KO |

## 5.2    Ascend C支持上板单步调试模块——断点管理模块功能设计

### 5.2.1    功能描述

该模块主要在lldb原断点设置功能的基础上，补充区分用户在device侧设置断点的逻辑，并在server端通过设备交互模块与设备进行通信，完成软断点/硬断点在设备上的设置。

### 5.2.2    处理流程描述

![img](../pic/3ee83363383be95362ca1d0ec9a6d074_775x483.jpg@900-0-90-f.jpg)

**断点设置流程**

1、 用户下发命令，命令交给CommandObjectBreakpoint类进行解析

2、 解析后的内容传递给Breakpoint类，包含断点类型、位置等信息

3、 根据DWARF信息解析具体的断点位置，转换为pc地址

4、 根据pc地址创建BreakpointSite，这里还需要根据断点的位置为断点设置架构信息

5、 将BreakpointSite交给ProcessGDBRemote，用于发送给服务端

6、 从BreakpointSite中提取地址、断点类型、架构，封装成packet发送到server端。 此处的packet拓展lldb自带的断点协议，在Z字头报文最后加上一个代表架构的枚举值、

7、 GDBRemoteCommunicationServerLLGS类接收到报文后，从报文中解析出地址、断点类型、架构等信息，交给AscendProcessLinux类处理

8、 AscendProcessLinux中的SetBreakpoint函数根据架构进行区分，如果是ascend的架构则使用设备交互模块中的DeviceContext，完成设备上断点的设置，反之则走NativeProcessLinux中的lldb原流程。

### 5.2.3    关键函数描述

1、 Target::CreateBreakpointSite

用于创建BreakpointSite的函数，这个地方是最开始区分device侧和host侧断点的位置。

断点的地址会携带一个section对象，这个对象标识了这个断点对应的位置位于程序的哪个段，我们通过这个section中的GetModule可以获取到这个段对应的Module，也就是这个程序中的哪一个.o文件，Module中会提供获取对应架构的方法，来帮助我们区分这个断点是设置在host侧还是device侧，我们在这里会将这个架构信息存储在BreakpointSite对象中，以方便后面进行区分。

2、 AscendProcessLinux::SetBreakpoint

该函数需要通过设备交互模块完成断点的设置。

其中硬断点的设置直接调用DeviceContext中的SetHardBreakpoint即可

软断点的设置分以下步骤：

1)   ReadMemory读取对应断点位置的指令并保存

2)   WriteMemory将断点指令覆盖到对应的pc位置

3)   InvalidCache来重置设备侧的指令Cache。

### 5.2.4    数据描述

采用的Packet结构: Z{type},{addr},{length},{arch}

type:断点类型的枚举值

addr:断点设置的pc地址

length:断点对应指令的长度

arch:断点对应的架构枚举值

### 5.2.5    错误处理

当SetBreakpoint失败时，打印日志：

```
    Set ascend breakpoint on {addr} failed, reason is: {DeviceContext返回信息}
```

其余模块的处理和lldb原逻辑保持一致

### 5.2.6    测试设计

1、 正常路径

| 测试场景           | 测试方案                                       | 预期结果                                           |
| ------------------ | ---------------------------------------------- | -------------------------------------------------- |
| 设置host断点       | 使用lldb设置host侧代码断点，并运行             | 提示设置成功，并且能够断住，正确打印断住时的代码段 |
| 设置device断点     | 使用lldb设置device侧代码断点，并运行           | 提示设置成功，并且能够断住，正确打印断住时的代码段 |
| 删除host断点       | 使用lldb删除设置的host侧代码断点，并运行       | 运行后不再断住                                     |
| 删除device断点     | 使用lldb删除设置的device侧代码断点，并运行      | 运行后不再断住                                     |
| 去使能host断点     | 使用lldb去使能设置host侧代码断点，并运行       | 运行后不再断住                                     |
| 去使能device断点   | 使用lldb去使能设置device侧代码断点，并运行       | 运行后不再断住                                     |
| 重新使能host断点   | 使用lldb重新使能无效的host侧代码断点，并运行   | 断点重新生效，运行后能断住，正确打印断住时的代码段 |
| 重新使能device断点 | 使用lldb重新使能无效的device侧代码断点，并运行 | 断点重新生效，运行后能断住，正确打印断住时的代码段 |

2、 异常路径

| 测试场景                             | 测试方案                                      | 预期结果                             |
| ------------------------------------ | --------------------------------------------- | ------------------------------------ |
| 设备连接失败的场景下设置device侧断点 | 构造DeviceContext返回异常的场景，然后设置断点 | 提示设置失败，打开日志能看到具体原因 |

## 5.3    Ascend C支持上板单步调试模块——变量读写模块功能设计

### 5.3.1    功能描述

该模块主要在lldb原变量、寄存器读写功能的基础上，补充区分用户读写device侧内存的逻辑，同时在server端与设备交互模块通信，调用读写内存、寄存器的相关接口，来完成变量的读写。当前在device侧仅支持变量的读取。支持读取bf16、half, tf32数据类型，支持展示指定shape的数据。

### 5.3.2    处理流程描述

**变量打印处理流程**

![img](../pic/1d6a84b7f368301aa0e1c164d07fcdeb_693x497.gif@900-0-90-f.gif)

1、 用户下发变量打印命令，由CommandObjectExpression接收处理命令

2、 Evaluate解析要打印的变量，从DWARF的debug-info信息中提取对应变量的AddressClass和OPCode，其中AddressClass标识该变量存储的地址类型，比如UB、GM等；OPCode标识该变量地址的存储位置。

3、 ProcessGDBRemote::DoReadRegister接口接收到从OPCode中解出需要读的寄存器id后，封装成packet

4、 向server发送packet

5、 Server接收到packet后，从中解出寄存器id，然后调用AscendProcessLinux类中的DoReadRegister去读取寄存器中的值

6、 AscendProcessLinux调用设备交互模块提供的接口读取具体的值

7、 ProcessGDBRemote::DoReadMemory接口接收到寄存器的值后，Evaluate函数再通过寄存器的值+偏移量去计算要读的地址

8、 ProcessGDBRemote将地址封装成packet

9、 向server发送packet，该处我们拓展原来的x协议，在最后加上架构信息

10、      Server接收到packet后，调用AscendProcessLinux类中的DoReadMemory去读内存中的值

11、      AscendProcessLinux调用设备交互模块提供的接口读取具体的值

从debug_info中，解析变量读取逻辑的示意图如下，以变量“aaa”为例，其类型为int，地址的计算方式为：从栈基地址（fbreg寄存器中存放的地址）偏移28字节，该地址所在内存空间由address class指明，0x40含义是其位于内存空间Device Local中，代表其位于栈空间上，栈空间实际所在的内存空间在不同的芯片中有不同的设置，如下表所示。在Ascend910B上，则从Global Memory中读前述计算得出的地址后4个字节，则可得出变量“aaa”的地址。

![image-20251216185026353](../pic/4f2a6ccd25f64b91bf6ea8a08c9bef04_554x539.png)

| 芯片型号   | 栈空间所在内存空间 |
| ---------- | ------------------ |
| Ascend910B | Global Memory      |
| Ascend310P | Scalar buffer      |

### 5.3.3    关键函数描述

1、 ProcessGDBRemote::DoReadRegister

原的lldb读取寄存器，需要依赖对架构上的整套寄存器进行建模，这种方式有着过高的成本。所以我们在lldb中新增一条通过单寄存器id读取寄存器值的通路。

该接口会新增协议qDeviceRegister,{id}，向新增的server接口发送消息，然后server侧的接口再根据id通过设备交互模块访问寄存器。

2、 DwarfExpression::Evaluate

该函数中需要对几个典型的OPCode做特殊处理，去通过module来区分架构，然后把流程适配到device的场景。目前识别到的比较常见的OPCode有DW_OP_bregx与DW_OP_fbreg。

DW_OP_bregx:表示该对应变量的地址，存储在这个操作符后面跟着的id对应的寄存器中。

DW_OP_fbreg:表示该对应变量的地址，由帧地址寄存器再加上后面跟着的偏移量计算得到。

在ascend场景下，寄存器id – 64，就能对应上设备上的X0-X31通用寄存器，其中X30寄存器为帧地址寄存器。

同时在该函数中，还需要将变量信息中的AddressClass提取出来，用于拼装packet。

3、 ProcessGDBRemote::DoReadMemory

该类在拼装协议时，需要补上arch和addr_type的信息。均通过新增参数传入。

4、 lldb_private::DumpDataExtractor

在用户使用memory read命令时，该函数用于判断数据类型信息，可对其进行数据类型的扩展，half，bf16，tf32，half[]，bf16[]，tf32[]

5、 ProcessGDBRemote::ReadDeviceRegister(uint32_t register_id, uint64_t &value) 

根据register_id读取寄存器，直接通过设备交互模块去ts读取值

6、 uint32_t Args::StringToDeviceRegister(llvm::StringRef s, uint8_t device_type)

根据寄存器名字和芯片类型，获取对应的寄存器号

### 5.3.4    数据描述

1、 新增的读取寄存器的协议

```
qDeviceRegister,{reg_id}
```

reg_id即为要读取的寄存器的id

2、 补充读取内存的协议

```
x,{addr},{size},{arch},{addr_type}
```

addr为地址

size为读取的大小

arch为读取的架构对应的枚举值

addr_type为读取的内存类型对应的枚举

3、 新增读取寄存器的参数选项—ascend

```
register read {reg_name} –ascend
```

### 5.3.5    错误处理

当从设备读取寄存器失败时，打印日志：

```
    Read ascend register {reg_id} on {core_id} failed, reason is: {DeviceContext返回信息}
```

当从设备读取内存失败时，打印日志：

```
    Read ascend memory {addr_type}:{addr} on {core_id} failed, reason is: {DeviceContext返回信息}
```

其余模块的处理和lldb原逻辑保持一致

当使用读取device寄存器失败时，终端输出打印需要包含：

```
read ascend register failed
```

当读取的寄存器名字不存在时，终端输出打印需要包含：

```
in xxx device, register name {} not exist
```

### 5.3.6    测试设计

1、 正常路径

| 测试场景                                        | 测试方案                                                     | 预期结果           |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------ |
| 使用p命令打印全局变量                           | 断点断住后，使用p命令打印全局变量(GM\UB\L1\L0A\L0B\L0C)      | 能够正确打印       |
| 使用p命令打印LocalTensor                        | 断点断住后，使用p命令打印LocalTensor                         | 显示出Tensor信息   |
| 使用x命令打印对应内存类型的地址                 | 断点断住后，使用x命令打印对应内存类型的地址    –m (GM\UB\L1\L0A\L0B\L0C)  -f (float16[],bf16[], half[], tf32[])  --size (128, “1,2,3”) | 能够正确打印       |
| 使用register read打印对应的寄存器               | 断点断住后，使用register read xx---ascend命令打印对应寄存器  | 能够正确打印       |
| 使用register read显示当前设备能打印的寄存器名字 | 断点断住后，使用register read –a--ascend命令显示能打印的寄存器 | 能够显示寄存器名字 |

2、 异常路径

| 测试场景                                          | 测试方案                                                     | 预期结果                                 |
| ------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------- |
| 设备连接失败的场景下进行设备侧打印                | 构造DeviceContext返回异常的场景，然后在断点生效后打印变量    | 提示变量打印失败，打开日志能看到具体原因 |
| 断点在host上时，使用register read xxx –device命令 | 断点在host侧后，分别使用register read –a –ascend、register read xxx --ascend | 提示打印失败                             |

## 5.4    Ascend C支持上板单步调试模块——进程控制模块功能设计

### 5.4.1    功能描述

1. 基于RTS接口，感知Device程序状态变化。

2. 基于RTS接口，控制Device程序继续执行。

3. ctrl-c时，支持device侧代码停住

4. device侧遇到中断时，用户后续可以进行单步按行调试

### 5.4.2    处理流程描述

![img](../pic/f49fd6796ed2b8f66fa66b71c965f1e0_692x562.gif@900-0-90-f.gif)

**device****中断以及恢复流程图**

1. device遇到断点触发中断，lldb-server发送packet通知lldb client

2. lldb client接收到packet后，展示中断信息

3. 用户命令执行continue

4. lldb-client发送取消当前断点的packet

5. lldb-server修改device内存还原对应内存地址的内容

6. lldb-client发送单步指令执行的packet

7. lldb-server调用device context的单步指令接口

8. lldb-client发送恢复刚才断点的packet

9. lldb-server修改device内存，写入中断指令

10. lldb-client发送恢复进程的packet

11. lldb-server调用device context的resume接口，接着跑device进程

![img](../pic/1e8f351b1656beee283d3fb8f13f8ca6_789x378.gif@900-0-90-f.gif)

**ctrl-c****处理流程图**

1. 用户命令行ctrl-c，lldb发送packet给lldb-server

2. lldb-server收到packet后，给用户进程发送中断信号

3. 子进程的信号触发了父进程lldb-server 监测线程，触发host中断处理流程

4. host ctrl-c中断流程里，触发调用device的task kill接口

5. host ctrl-c中断处理流程进入device ctrl-c中断处理流程  等待device task kill的响应

6. ts device task kill 结束后，上报此时device中断的core id, core pc, core type等信息

7. device ctrl-c中断处理流程发送device中断给lldb

8. lldb收到ctrl-c的pc等信息后，显示对应的device代码内容

![image-20251216185123654](../pic/0ca7b64e6a944b2bc9ed1ba758766b7c_554x786.png)

1、 用户拉起算子，遇到device断点后停下

2、 用户设置模式：单步时，只针对当前核还是所有核模式，默认是针对所有核模式（这是为了防止不用单步时保持resume/single step功能，默认模式也可以反过来）

3、 用户命令按step over

4、 lldb会走到反汇编模块，根据此时中断位置，判断是aiv/aic/host

5、 基于中断位置，dlopen hiipu64 capi模块并使用指令解析功能，获取指令是否为分支/Call

6、 在下个为branch的指令地址设置断点

7、 指定为某些core做resume操作，使得他们继续运行，直到遇到断点，上报断点信息

8、 指定为某些core做single step操作，执行branch指令

9、 然后接着重复7/8动作，直到下一行代码行

10、 展示代码行信息

### 5.4.3    关键函数描述

1、AscendProcessLinux::HandleProcessState

使用DeviceContext监测线程收到Device中断消息时，回调这个函数。该函数会设置进程状态，发送消息回lldb客户端。

2、AscendProcessLinux::ResumeDevice 

用于恢复Device侧进程，基于DeviceContext::的Resume接口。会恢复所有core，进行继续运行。

3、 AscendProcessLinux::MonitorSignal

当device context上报task kill中断时，触发这个callback函数，设置好stop info信息

4、 AscendProcessLinux::SetStoppedBySignal

重载NativeThreadLinux::SetStoppedBySignal，该函数负责发送task kill并等待task kill上报中断，有阻塞行为，并设置超时。

5、 DisassemblerLLVMC::MCDisasmInstance::GetMCInstSimply

这个函数用于替换所有调用DisassemblerLLVMC::MCDisasmInstance::GetMCInst的地方，原是调用llvm的getInstruction接口获得反汇编的指令大小和llvm::MCInst。新的函数基于以下c api实现：

c api接口定义如下：

```c
 enum Flag {
 CanBranch = 0,

IsCall
 HasDelaySlot
 IsLoad

IsAuthenticated
 };

 /*
 \* Args:
 \* features: 支持dav-c220-cube, dav-c220-vec
 \* opcode_data: 待解析的指令数据
 \* opcode_data_len: 待解析的指令数据长度
 \* pc: 当前pc值，offset

*flag: 判断指令的bit mask, 哪一位为1，则表示true，比如第1位表示CanBranch，第二位表示IsCall

*inst_size：表示指令解析后的指令大小是多少

 \* Returns:
 \* 0: Fail
 \* 1: SoftFail
 \* 3: Success
 *
 */
 uint8_t GetInstruction(const char *features, const uint8_t* opcode_data, const size_t opcode_data_len, uint64_t pc, enum Flag *flags, uint *inst_size); 
```

6、 class CommandObjectAscendAiv : public CommandObjectParsed 

新增ascend set run-mode=1

默认情况下，continue、step等命令是针对所有核；

run-mode=1后，continue, step等命令只针对当前核

### 5.4.4    错误处理

1.   若ctrl-c时，device还未运行，task kill接口应返回失败，并打印warning日志

2.   其他错误处理与lldb原逻辑保持一致。

### 5.4.5    测试设计

**正常路径**

| 测试场景                             | 测试方案                                                     | 预期结果                                                     |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 断点生效                             | 拉起算子，设置断点，按命令run                                | 能够正常停在指定代码行                                       |
| 断点情况下继续运行，命中下一个断点   | 在停在循环语句里的断点位置情况下，按continue；               | 再次命中断点                                                 |
| 断点取消、继续运行到程序退出         | 断点断住后，取消断点，再按c                                  | 程序运行到结束                                               |
| 程序还未运行到device侧时，使用ctrl-c | 可以在host代码写个while循环，拉起程序后，按ctrl-c            | 程序中断在host侧，并显示代码行                               |
| 程序运行到device侧时，使用ctrl-c     | 可以在device代码写个大计算量的代码，拉起程序后，按ctrl-c     | 程序中断在device侧，并显示代码行                             |
| device侧断点执行多核单步命令         | 算子程序在device代码上设置断点，断点触发后，多次按n命令，使用ascend info cores查看n 前后aicore的变化 | 程序按代码行正确执行下去，能正常显示代码行，n前后所有core的pc都应该发生变化 |
| device侧断点执行单核单步命令         | 算子程序在device代码上设置断点，断点触发后，先按ascend set -mode=1，然后多次按n命令；使用ascend info cores差看单步前后，是否只有当前core的pc发生变化 | 单步命令前后，只有当前core pc发生变化                        |
| host侧断点执行单步命令               | 断在设置在host代码后，执行，多次按n                          | host代码单步现象正常                                         |

**异常路径**

| 测试场景                                       | 测试方案                                 | 预期结果                               |
| ---------------------------------------------- | ---------------------------------------- | -------------------------------------- |
| 算子跑到device侧使用ctrl-c后，使用continue命令 | ctrl-c使得中断在device侧后，使用continue | 算子跑完退出，此时device侧程序无需恢复 |

## 5.5    Ascend C支持上板单步调试模块——状态信息展示模块功能设计

### 5.5.1    功能描述

1. 基于RTS接口，获取task/block/stream的展示

2. 支持kernel launch信息的展示

3. 支持aicore切换时的代码上下文展示

4. 支持所有核的上下文展示

### 5.5.2    处理流程描述

![img](../pic/a0dc3ea788930f113ab406e9c09435ae_693x694.gif@900-0-90-f.gif)

**ascend info/ascend core****命令处理流程图**

![img](../pic/dedf88cf812b151ec963ac9d077b8519_692x676.gif@900-0-90-f.gif)

**Core****的状态信息查询流程图**

### 5.5.3    关键函数描述

1、Status AscendProcessLinux::GetCoresInfo(std::vector<CoreInfo> &info)

使用DeviceContext获取算子用到的所有core的信息，返回结果用于客户端组装展示信息使用。

2、bool CommandObjectAscendAiv:: DoExecute(Args &command, CommandReturnObject &result) 

1. 用于切换到aiv，lldb client / lldb server侧都会维护当前的core_id, core_type值。用于读取寄存器、内存。

2. 刷新client保存的寄存器缓存、stack frame的frame base pc, pc等信息

3. 调用展示代码信息的相关函数，来刷新客户界面的代码信息

切换aic的函数也是同理设计。

3、StackFrame::GetFrameBaseValue

  该函数用于调试器获取栈基地址，当切核后，我们需要让StackFrame类的m_flags变量里的缓存失效，重新触发该函数进行基地址解析。

4、StackFrameList::GetFrameAtIndex(uint32_t idx)

该函数用于获取StackFrame栈帧信息，但是有缓存，我们需要先调用frame_sp->GetThread()->GetRegisterContext()->InvalidateAllRegisters();使得寄存器缓存失效，然后获取PC寄存器更新StackFrame的pc值。

5、StopInfo::GetDescription

该函数用于获取线程停下来的原因描述，可以区分开breakpoint和step over的描述信息。如果我们用StopReason，里面的枚举类型是无法区分的，因为breakpoint 和step over本质都是断点停止。另外，对于每次中断，client端都能收到中断信息，此时我们只知道一个core的中断原因，其他core的原因需要在client完成，即根据pc值比较，同样的pc，用同样的原因，默认用trace，如果pc不同，尝试在breakpoint里找这个pc，找到则为breakpoint。

### 5.5.4    数据描述

```C++
struct CoreInfo {
uint8_t core_id;
uint8_t reserve;
uint16_t total_num;
CoreType core_type; // aic / aiv
uint32_t stream_id;
uint32_t task_id;
uint32_t block_id;
uint32_t status; // device进程状态信息： step_over, breakpoint, step in, step out, trace
uint64_t pc; // 当前aicore pc位置
};

struct TaskInfo {
uint32_t stream_id;
uint32_t task_id;
uint32_t device_id;
string kernel_name; 
};

struct StreamInfo {
uint32_t stream_id;
uint32_t device_id;
CoreType core_type; // aic / aiv
};

struct BlockInfo {
uint32_t stream_id;
uint32_t device_id;
uint32_t task_id;
uint32_t block_id;
};
```

### 5.5.5    错误处理

1.   获取task/block/stream失败时，显示报错信息

2.   切到不是该task的core时，显示invalid core id, use “ascend info cores” to see which core id can choose

### 5.5.6    测试设计

| 测试场景                             | 测试方案                            | 预期结果                                                   |
| ------------------------------------ | ----------------------------------- | ---------------------------------------------------------- |
| 算子进程命中断点后，lldb始终显示状态 | Lldb调试用户进程，设置断点后，按run | run显示kernel name信息                                     |
| 算子进程命中断点后                   | Device断点停住后  ascend info tasks | 展示device_id/stream_id/task_id/kernel_name信息            |
| 算子进程命中断点                     | ascend info stream                  | 展示 device_id/stream_id/core_type信息                     |
| 算子进程命中断点                     | ascend info blocks                 | 展示device_id/stream_id/task_id/block_id信息               |
| 加载算子并运行                       | msdebug 加载算子  按run             | 算子拉起时启动时展示kernel launch信息                      |
| 算子进程命中断点                     | ascend info codes                   | 展示所有核停下来时候，对应的代码行信息，每个核单独一块代码 |
| 算子进程命中断点                     | ascend aic 1  ascend aiv 1          | 当使用切核命令时，刷新代码展示信息到当前核                 |

## 5.6    Ascend C支持上板单步调试模块——调试使能模块功能设计

### 5.6.1    功能描述

本模块支持：

1)    在以下算子调用方式与调用场景中，获取算子kernel object二进制段与运行时信息，并在算子kernel被执行之前使能调试功能。使能调试功能包括加载算子kernel中包含的DWARF信息与完成算子核函数断点设置。

a)    支持以下算子调用方式：

​           i.      使用算子运算符（<<<>>>）调用算子；

​          ii.      使用aclnn框架静态或动态调用算子；

​         iii.      使用runtime接口调用算子；

b)    支持以下算子kernel object部署场景：

​           i.      算子部署在fatbin中（与可执行文件链接在一起）；

​          ii.      算子部署在动态库中；

​         iii.      算子部署在CANN目录aclnn框架中；

​         iv.      算子部署在本地任意目录，使用runtime接口直接加载；

​          v.      容器场景；

2)    多kernel算子拉起时，针对指定kernel使能断点配置并命中断点进入调试交互界面。

a)    指定调试算子kernel的方式：对期望调试的算子kernel核函数设置断点；

### 5.6.2    处理流程描述

调试器使能调试功能之前即算子kernel被运行之前，需要获取两大类信息：算子kernel object二进制段与算子运行时信息。

前者提供算子代码的DWARF（Debugging With Arbitrary Record Formats）信息，用于：

1)    解析断点位置，并转换为PC偏移值；

2)    提供变量解析方法；

后者提供算子运行时确定的相关设备信息，用于在运行时完成算子调试功能使能，比如设置断点、读取变量等，算子的运行时信息包括：

1)    device id，算子运行所在的设备id；

2)    stream id，算子所在流的id；

3)    pid，算子进程的全局pid（host）；

4)    kernel name，算子名；

5)    pc start address，加载算子二进制的内存首地址；

#### i.      算子kernel object二进制段获取

算子kernel object二进制段获取方式与算子部署场景有关，如下图所示，

![img](../pic/1407b4f6732b89853cb9c69dce685909_692x365.gif@900-0-90-f.gif)

1)    当算子部署在fatbin中时，可直接解析该可执行文件，提取特定的段内容（.aicore_binary或其他衍生段）即可获取算子kernel object二进制段；

2)    当算子部署在动态库中时，可遍历可执行文件所链接的所有动态库，寻找并提取包含算子特定的段即可获取算子kernel object二进制段；

3)    当算子部署在PyTorch框架中或算子直接通过runtime接口拉起时，在代码运行时才决定加载具体的算子kernel object二进制，同时该场景可能出现连续调用多个算子，因此该场景下约束用户输入所需要调试的特定算子路径，调试器直接从所给出的算子路径获取算子kernel object二进制；

获取算子kernel object二进制段方法与算子是否部署在docker中运行无关，当任意一种部署场景下成功解析到算子kernel object二进制之后，不再尝试进行其他场景kernel object二进制获取。

#### ii.      算子kernel运行时信息获取

算子运行时信息获取方法与算子调用方式有关，三种算子调用方式对应的运行时runtime接口调用流程如下图所示，运行时信息按照如下方式获取：

![img](../pic/e670491ba4d416621fca67f4abef2f70_258x578.gif@900-0-90-f.gif)

![img](../pic/decd68350c765a77399e4d20378682b6_278x597.gif@900-0-90-f.gif)

![img](../pic/7e367e2118bac4120e86e3fc2da3204a_293x513.gif@900-0-90-f.gif)



1)    device id，可直接从rtSetDevice() / rtSetDeviceEx() / rtCtxCreateEx()接口入参中获取；

2)    stream id，算子所在流的id可通过运行时接口查询获得：rtGetTaskIdAndStreamIDFunc()；

3)    pid，考虑到在docker场景下，系统调用函数getpid()获取的算子进程pid不是全局pid，而是在容器环境下namespace中的pid，因此使用驱动接口drvDeviceGetBareTgid()获取全局pid；

4)    kernel name，在算子调用符与aclnn静态场景下，可通过rtFunctionRegister()接口入参处获取调用的算子核函数对应的函数名；在aclnn动态场景与runtime接口调用场景下，暂无法通过runtime接口直接获取，可直接解析算子kernel object二进制段，如下所示即为算子kernel object中所包含的多个核函数名，其尾部是tilingkey，因此可从rtKernelLaunchWithHandleV2接口中首先获取tilingkey，根据tilingkey在算子kernel object二进制段中匹配到实际加载的核函数名；

![image-20251216185305258](../pic/c42f725cb586fed3fa88000a618e8524_692x280.png)

5)    pc start address，加载算子二进制的内存首地址可通过该接口查询得到：rtKernelGetAddrAndPrefCnt()。向该接口传入算子kernel object中第一个核函数指针（算子调用符与aclnn静态场景）或第一个核函数的tilingkey（aclnn动态场景），即可查到加载算子二进制的内存首地址。算子调用符与aclnn静态场景下，如果算子有多个核函数，rtFunctionRegister()接口也会执行多次，每次注册一个核函数，因此可获取所有核函数的指针，查询这些所有核函数被加载的内存首地址，选择地址最小的一个即是所需的pc start address。aclnn动态场景下，直接解析算子kernel object二进制段，获取第一个核函数的tilingkey值，查询该tilingkey所对应核函数被加载的内存地址即是所需的pc start address。

算子运行时信息大部分来源于算子自行调用的runtime接口函数的入参，要获取这些函数入参，需劫持这些runtime接口，使调用这些函数的地方先跳转至调试器“伪造”的runtime接口中，完成所需的操作后，再调用“真正”的runtime接口，完成算子功能。实现方式可在一个单独的动态库libruntime_stub.so中定义相同的runtime接口，并通过LD_PRELOAD环境变量预加载，完成runtime接口劫持功能。

算子调用符与aclnn静态场景算子运行时信息获取流程：

![img](../pic/a877a023515a0477bddace6507e2d8bf_527x1059.jpg@900-0-90-f.jpg)

aclnn静态场景算子运行时信息获取流程：

![img](../pic/34e4ca82ac45d610be19b3079417c3d5_652x1047.jpg@900-0-90-f.jpg)

![img](../pic/8b9ec7d6f25b40ff9f44a295526367b7_538x1006.jpg@900-0-90-f.jpg)

#### iii.      指定特定算子kernel进行调试

当使用PyTorch框架的API实现算子调用脚本时，通常会调用到多个算子，调试器如要支持指定特定的算子进行调试，需定义如下的概念：

1)    算子kernel的独有标识；

2)    确定使能的算子kernel；

3)    使能特定算子kernel调试的时机；

首先，使用加密算法（比如SHA256）对算子kernel object文件进行哈希计算，获取一个独有的哈希值来标识该算子kernel。不使用算子kernel文件的文件系统路径作为标识的原因在于，用户本地调试算子时，虽然把算子kernel object文件已部署到CANN框架中，但不清楚具体部署的位置，所以依然可能指定一个本地build目录下的kernel object文件，虽然这个文件与部署到CANN框架下的文件完全一致，但在文件系统中的路径不一致。同时，因算子kernel object的文件名也可被随意修改，无法保证不与其他算子kernel object同名，因此也不能直接使用文件名作为标识。

其次，确定使能哪一个算子kernel的方法是，当用户设置的断点位置匹配到算子kernel object中的调试信息时，我们认为用户期望使能该kernel。当累计有多个断点匹配到了不同的算子kernel时，取最后设置的断点对应的kernel作为期望使能的算子kernel，如此，理论上用户完成一个算子kernel调试后，再次设置下一个算子kernel的断点，可继续完成调试。

最后，使能特定算子kernel调试的时机关键在于完成device断点设置的时机。在接收用户输入的断点信息后，若不向device下发断点，则所有算子kernel均不会命中断点停下，算子会直接运行至结束，调试器不会向用户提供交互界面对该算子进行调试，即调试器去使能了对算子kernel的调试。而对用户指定的算子kernel进行device断点设置的时机是：算子kernel已完成前置动作，执行rtKernelLaunch()等系列接口前。因此，调试器需要劫持rtKernelLaunch()等系列接口，在每个算子kernel调用该函数前，告知调试器本次调用的算子kernel的标识，若标识与用户指定的算子kernel匹配，那么调试器即按照该算子kernel的运行时信息配置device断点，完成配置后通知算子kernel继续运行，直到命中断点。

一个简易的使能特定算子kernel的调试流程为，算子调试信息导入后，用户对该算子kernel代码设置断点，断点完成匹配，并生成该算子kernel object的hash值保存，此阶段发生在调试器客户端侧。在用户输入run命令后，客户端把hash值发送至服务端，同时，被调试程序也完成加载的算子kernel object文件的hash值计算，并发送至调试器服务端。服务端进行hash值匹配，若匹配成功，则在设置断点时，允许进行算子指令覆盖，否则则忽略。在被调试程序反注册算子kernel object后，也应通知服务端删除该算子对应的hash值。

完整的流程处理如下图所示：

![img](../pic/827497b6910a602b4410272e480d19ee_638x1069.jpg@900-0-90-f.jpg)

典型场景：

1)    PyTorch API通过aclnn接口依次调用算子A、B、C、B，使用命令导入算子B的kernel object文件的调试信息后，在算子B的核函数中设置断点位置并开始调试，算子A被拉起后，调试器此时识别到算子A与导入的算子调试信息不匹配，因此不使能调试功能；算子B被拉起后，调试器识别到算子信息匹配，使能调试功能，在算子B完成调试运行结束后，去使能调试功能；算子C被拉起后，算子调试信息不匹配，不使能调试功能；算子B再次被拉起，算子信息匹配，使能调试功能；

2)    PyTorch API调用动态库提供的接口，接口内部使用<<<>>>调用算子，依次调用算子A、B、C、B，未显式导入算子kernel object文件调试信息，在算子B的核函数中设置断点位置并开始调试，后续流程同场景1；

3)    PyTorch API调用动态库提供的接口，接口内部使用aclnn接口调用算子，依次调用算子A、B、C、B，未显式导入算子kernel object文件调试信息，在算子B的核函数中设置断点位置并开始调试，后续流程同场景1；

### 5.6.3    关键函数描述

1.  std::shared_ptr<ModuleSpec> ObjectFileELF::GetChildModuleSpec

调试器从已经加载的ELF文件里获取.aicore_binary的段，读取该段，后续用于设置断点、展示代码信息

2.  DynamicLoaderPOSIXDYLD::RefreshModules

当算子二进制加载所需的.so时，调试器会在这个函数刷新module，此时可以对每个新增的.so查看是否有.aicore_binary，如果有，也加载为新的module信息

设置断点、展示代码信息

3.  Target::SetExecutableModule

当调试器拉起被调试程序时，在该函数中读取环境变量指定的算子调试信息路径，并调用函数1进行解析。

### 5.6.4    数据描述

从被调试程序获取的算子kernel运行时信息结构由如下组成，

```C++
struct OpRtInfo {
​    int32_t deviceId;
​    int32_t streamId;
​    int32_t pid;
​    uint64_t pcStartAddr; 
​    std::string kernelName;
​    std::string kernelHash;
}
```

### 5.6.5    错误处理

触发错误后按照如下原则进行处理：当错误不影响调试使能时，如未查询到用户指定的断点，仅打印日志提示用户；当错误导致调试功能无法使能时，如打开驱动失败、运行时信息获取失败等，抛出异常终止调试。

1)    当可执行文件和环境变量里都没有kernel二进制数据信息时，打印日志提示，原则上cpu代码调试可不需要算子kernel object二进制信息；

2)    当环境变量指向的路径不存在时，界面打印报错；

3)    当用户指定的断点不存在时，打印提示用户；

4)    当未获取到runtime库接口函数指针时，抛出异常终止调试，界面打印报错；

5)    当查询算子运行时信息失败时，抛出异常终止调试，界面打印报错；

6)    当调试器打开驱动失败、通过驱动下发断点失败时，抛出异常终止调试，界面打印报错；

7)    其他lldb内部错误沿用lldb开源代码处理流程；

### 5.6.6    测试设计

| 测试场景                                                     | 测试方案                                                     | 预期结果               |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------- |
| C++直接<<<>>> 拉起算子，算子打包在fatbin中                   | 使用C++工程编译出二进制文件，进行断点、变量打印调试          | 断点、变量功能打印正常 |
| python pytorch框架拉起aclnn封装的算子，算子文件独立存放      | 使用python pytorch拉起aclnn算子，手动导入算子调试信息，进行断点、变量打印调试 | 断点、变量功能打印正常 |
| python pytorch框架拉起<<<>>>封装的算子，算子打包在动态库中   | 使用python pytorch拉起<<<>>>算子，进行断点、变量打印调试     | 断点、变量功能打印正常 |
| python pytorch框架拉起aclnn封装的算子，算子打包在动态库中    | 使用python pytorch拉起aclnn算子，进行断点、变量打印调试      | 断点、变量功能打印正常 |
| 调试器打开驱动失败                                           | 移除驱动设备节点后，使用C++工程编译出二进制文件，进行断点、变量打印调试 | 运行后抛出异常终止调试 |
| runtime库接口函数指针获取失败                                | 移动runtime库文件位置后，使用C++工程编译出二进制文件，进行断点、变量打印调试 | 运行后抛出异常终止调试 |
| 驱动初始化调试使能模式失败                                   | 使用较老的驱动包后，使用C++工程编译出二进制文件，进行断点、变量打印调试 | 运行后抛出异常终止调试 |
| 算子运行时信息获取失败                                       | 使用C++工程编译出二进制文件，进行断点、变量打印调试，打桩pcStartAddr获取函数，构造失败 | 运行后抛出异常终止调试 |
| 使用已被占用的device进行调试                                 | 使用C++工程编译出二进制文件，进行断点、变量打印调试，不退出，再次拉起，进行断点、变量打印调试 | 运行后抛出异常终止调试 |
| 依赖的CANN环境变量未找到                                     | 手动清空环境变量$ASCEND_TOOLKIT_HOME的值，使用C++工程编译出二进制文件，进行断点、变量打印调试 | 运行后抛出异常终止调试 |
| python pytorch框架拉起多个aclnn封装的算子，算子文件独立存放，指定特定算子调试 | 使用python pytorch拉起aclnn算子，手动导入算子调试信息，进行断点、变量打印调试 | 断点、变量功能打印正常 |
| python pytorch框架拉起aclnn封装的算子，算子打包在动态库中，指定特定算子调试 | 使用python pytorch拉起aclnn算子，手动导入算子调试信息，进行断点、变量打印调试 | 断点、变量功能打印正常 |

## 5.7    Ascend C支持上板单步调试模块——机机接口模块功能设计

### 5.7.1    功能描述

本模块提供机器友好的调试交互接口，该接口一方面接收外部客户端插件发送来的调试命令，指示调试器执行特定操作，比如设置断点；另一方面，该模块在处理完调试命令后，以结构化的文本格式向外部客户端传输程序状态、变量等调试相关信息。

功能列表：

1)  支持接收外部输入的调试命令并解析执行；

2)  支持构造结构化的文本信息向外部返回调试结果；

该模块（lldb-mi）可等价替代lldb客户端，从外部接收调试命令，向调试器server发出调试命令，与原lldb客户端不同的是，原本按照人类友好格式输出的调试结果，比如断点、变量信息会按照特定的结构化文本信息流返回外部，易于供外部机器解析。

### 5.7.2    处理流程描述

![img](../pic/5a98d91e7231ca7325e9703aedcf55a4_692x456.jpg@900-0-90-f.jpg)

因调试器在核函数调试继承了在CPU侧调试的命令，机机接口对外可直接沿用GDB-MI协议。因命中核函数断点后，调试器还额外实现了其他定制化命令与打印输出，因此需要在命中核函数断点时，在断点描述文本结构中进行差异化区分，为不影响原有结构元素的处理逻辑，建议直接新增一个字段表征是否命中算子核函数断点。

最终的可视化效果应包含以下功能：

1)    程序控制，包括运行、暂停、恢复、单步、步进、步出；

2)    变量展示，包括默认显示局部变量，手动展示全局变量与类成员变量；

3)    内存展示，支持GM/UB/L0/L1内存在IDE中展示，展示格式支持int64/int32/int16/int8/uint8/fp64/fp32/fp16/bf16；

4)    多核调试，支持在IDE中展示当前核信息，并支持图形化输入核切换命令，核切换前后，新的核所处的断点位置均处于高亮状态；

5)    单步调试，支持step over/in/out命令按钮；

6)    寄存器展示，支持在IDE中展示寄存器信息；

![img](../pic/bb84025f9b5a4c2d987803d66426d571_692x374.jpg@900-0-90-f.jpg)

### 5.7.3    关键函数描述

1.   

![image-20251216185342895](../pic/68be244b13376d233614bf8eb331234d_685x273.png)

当被调试程序命中断点后，lldb-server通知lldb-mi处理断点状态，lldb-mi进入该函数的eStopReasonBreakpoint分支，向stdout打印信息通知客户端，进入断点命中状态，同时输出结构化的断点描述文本。

当命中算子核函数的断点时，相比命中普通断点，调试器支持更多定制化命令，为区分两种断点场景，调试器本身新增了枚举值eStopReasonDeviceBreakpoint，因此在该函数中也新增一个分支处理该枚举值对应的核函数断点场景，并通知外部客户端当前进入了eStopReasonDeviceBreakpoint状态。 

2.    

![image-20251216185359642](../pic/dbfa34a1f3f53d9d818e86cebc593f94_683x325.png)

lldb-mi使用该函数完成断点描述文本的构造，因核函数断点与普通断点遵循相同的结构属性，因此均沿用原始断点描述结构，为区分核函数断点与普通断点，新增一个字段用于区分，比如“is-device=true/false”。

### 5.7.4    数据描述

lldb-mi保持原gdb-mi协议向外部客户端输出结构化文本。当命中算子核函数断点时，断点描述文本按照如下格式定制化修改输出。

![image-20251216185415352](../pic/8e63502db399a28ba4c592bc5dc562e5_683x113.png)

### 5.7.5    错误处理

错误处理策略与原gdb-mi协议保持一致。

### 5.7.6    测试设计

| 测试场景                | 测试方案                                                     | 预期结果                                                     |
| ----------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 运行命中断点            | 在IDE中添加断点后点击运行                                    | 算子程序启动运行并高亮命中的断点，进入暂停状态               |
| 取消断点恢复运行        | 在IDE中取消设置的断点并点击continue                          | 算子程序恢复运行并运行至结束                                 |
| 查看局部变量            | 在IDE中命中断点后，查看VARIABLES栏中指定的变量               | VARIABLES栏中显示期望查看的变量，且值符合预期                |
| 查看成员变量            | 在IDE中命中断点后，在WATCH栏添加需要查看的成员变量           | WATCH栏中显示期望查看的变量，且值符合预期                    |
| 查看内存                | 在IDE中命中断点后，在WATCH栏添加Tensor类型的变量，并点击查看数据 | 弹出页面显示该Tensor变量所在内存中的值，可选择合适的数据类型展示 |
| 查看寄存器              | 在IDE中命中断点后，点击寄存器展示按钮                        | 弹出页面显示当前所在核的寄存器信息                           |
| 切核                    | 在IDE中命中断点后，点击右下角状态栏进入切核页面，输入需要切换的核id | 切换至期望的核，且IDE显示切核后对应的代码行                  |
| 单步运行                | 在IDE中命中断点后，点击step over                             | 高亮代码行显示至下一行                                       |
| 步进                    | 在IDE中命中断点后，点击step in                               | 高亮代码行显示到断点所在函数内部第一行                       |
| 步出                    | 在IDE中命中断点后，点击step out                              | 高亮代码行显示到断点所在函数外部第一行                       |
| 使用lldb-mi拉起算子调试 | 使用C++工程编译出二进制文件，进行断点、变量打印等调试命令    | 命中断点、变量打印等调试功能正常，且打印符合gdb-mi协议的结构化文本 |

# List of reference 参考资料清单

NA



























