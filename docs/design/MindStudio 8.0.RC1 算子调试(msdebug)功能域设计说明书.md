# **MindStudio 8.0.RC1 算子调试(msdebug)功能域设计说明书**

修订记录

| 日期 | 修订版本 | 修改描述 | 作者 |
| ---- | -------- | -------- | ---- |
|      |          |          |      |
|      |          |          |      |
|      |          |          |      |
|      |          |          |      |
|      |          |          |      |

[TOC]

# 1 算子调试(msdebug)功能域概述

名称：算子调试(msdebug)

描述：算子调试此处仅针对msdebug，也是与业内友商cuda-gdb对标的工具。针对该功能的意义：如果说，编译器建立了人类与机器之间的语言，使得我们能指挥机器按照我们的意图工作。那么，调试就是让我们理解机器的行为，建立了机器与我们之间的反馈渠道。只有编译和调试协同，才能让我们与设备有更好的协作，才能让我们的指挥更加顺畅。

# 2 算子调试(msdebug)功能域总体方案

调试器复用LLDB的设计，整体如下：

![img](../pic/0421583b68df8a356f223ff79a8f453d_653x285.gif@900-0-90-f.gif)

图3‑1 调试器(LLDB)的架构示意图

l  LLDB Debugger API及之上是调试工具对外的接口，比如：常见的命令行接口，与IDE对接的接口等。

l  LLDB Client(右下角) 会将人工输入的命令转换为机器识别的语言

−     Interpreter：用来解析输入的命令，将其转换为特定的Commands。

−     Commands：对应LLDB中的基础操作的抽象。

−     Data Formatters:用于将数据依照内置数据结构进行展示，比如：vector这种结构，用户关注的是内部存储的内容，需要支持这种格式展示。

−     Target所在的大框：被调试对象在客户端的代理，在客户端操作target后，其会通过GDB RSP协议将操作指令发给LLDB Server。

−     其他：客户端还有反汇编，二进制/符号解析等功能，用以辅助对程序的栈控制，运行状态控制，寄存器/内存读写，断点设置等系列功能。

l  LLDB Server：与被调试程序进行交互的主体，通过调用debug api实现功能。

整体方案中，除了调试器部分，现有CANN软件栈中缺乏debug API，需要在RTS中设计相关交互方案，实现调试器与昇腾芯片的交互。

结合具体的业务流程，组件间的协同关系如下：

![img](../pic/ad159e65963ea39b24015be8289a8b9d_657x602.jpg@900-0-90-f.jpg)

图4‑3 调试器实现断点/打印功能时序图

过程说明：

1：拉起用户进程，在子进程中设置LD_PRELOAD，使能桩函数，并阻塞（原有机制）子进程

2：用户在LLDB中设置断点，并保存信息（此时未真正下发断点到设备）

3： LLDB通知用户程序运行（原有机制）

4：当用户运行到set device时，通过接口的劫持，使得device Id上报到了LLDB

5：LLDB通过SQCQ通道给TS下发set debug，使得TS进入debug模式

6：当TS在debug模式下收到task时，通过SQCQ通道上报event，并返回base地址和deviceId

7：LLDB通过驱动的共享空间在device的kernel上覆写软断点指令

8: LLDB通过SQCQ通知TS断点设置行为，TS需要设置icache的缓存失效

9：LLDB通知TS继续执行

10：TS通过SQCQ上报**断点命中信息**，并停止对应核的指令调度

11：LLDB通过驱动申请GM内存

12：LLDB通过SQCQ通道通知TS将片上内存搬运到其申请的GM内存

13：LLDB将GM内存中的信息拷贝到host侧，并显示

14：LLDB将原断点指令恢复

15：LLDB通过SQCQ通知TS进行single step

16：LLDB通过驱动接口重新覆写软断点

17：LLDB通过SQCQ通知TS程序继续运行

# 3 算子调试(msdebug)功能域规格设计

本次仅支持基础功能，没有性能要求。需要支持如下交互能力：

```
lldb      add              # 利用LLDB拉起执行程序：
(lldb)b add.cpp:14         #输入断点; 此时回显断点信息
Breakpoint      1: where = xxxxx at add.cpp:14, address = 0x00000000e7
(lldb)run                     #启动程序，断点命中
*thread      #1, name=‘add’, stop reason = breakpoint 2.1
[Switching      focus to ascend kernel, device 0, vecId 0]
(lldb)ascend vecId 0      #后续针对vecId      0上的存储
[Switching      focus to ascend kernel, device 0, vecId 0]
(lldb)print xLocal  #此时显示对应变量的值
$1 =      {<tik2::BaseTensor<half>> = {<No data fields>}},      address_ = {dataLen = 1024, bufferAddr = 1024, absAddr = 0x},      shapeInfo_ = {shapeDim = 0, originalShapeDim = 0, shape = {32, 32, 32}, ….}
(lldb)x /4fh UB 1024#打印内存信息，现在Ascend      C的local      tensor都是UB
1.0      2.0 3.0 4.0
(lldb)continue#此时程序执行完成
Process      resuming
(lldb)q                     #此时退出LLDB

```

具体的支持接口规格如下：

表3-1 调试器支持规格

| **调试器支持的命令**         | **命令缩写** | **说明**                                                     |
| ---------------------------- | ------------ | ------------------------------------------------------------ |
| break                        | b            | NA                                                             |
| run                          | r            | NA                                                             |
| continue                     | c            | NA                                                             |
| quit                         | q            | NA                                                             |
| print                        | p            | NA                                                             |
| memory read                  | x            | 示例：x -m GM -f float16[]  0x00001240c0037000               |
| ascend aiv/aic [number]      | NA             | 切核，后续对于具体片上内存的打印以最近一次切核的对象为准     |
| ascend info [device/aicores] | NA             | 从硬件维度显示算子任务对昇腾芯片的占用                       |
| target create                | NA             | 加载core文件或者可执行目标文件，示例：  1. target create test  2. target create --core core.bin |
|                              |              |                                                              |

# 4 算子调试(msdebug)子功能域

## 4.1 调试器（msdebug）功能域概述

名称：调试器（msdebug）

描述：msdebug是基于LLDB开发的适配昇腾芯片的调试器，包含基本的断点设置、程序控制等。其本身通过调用debug API实现对芯片的控制。

## 4.2 调试器（msdebug）功能域总体方案

上板调试复用LLDB的设计，整体如下：

![img](../pic/3ad638f462ee2712a2334a42b41b070c_653x285.gif@900-0-90-f.gif)

图3‑1 调试器(LLDB)的架构示意图

l  LLDB Debugger API及之上是调试工具对外的接口，比如：常见的命令行接口，与IDE对接的接口等。

l  LLDB Client(右下角) 会将人工输入的命令转换为机器识别的语言

−     Interpreter：用来解析输入的命令，将其转换为特定的Commands。

−     Commands：对应LLDB中的基础操作的抽象。

−     Data Formatters:用于将数据依照内置数据结构进行展示，比如：vector这种结构，用户关注的是内部存储的内容，需要支持这种格式展示。

−     Target所在的大框：被调试对象在客户端的代理，在客户端操作target后，其会通过GDB RSP协议将操作指令发给LLDB Server。

−     其他：客户端还有反汇编，二进制/符号解析等功能，用以辅助对程序的栈控制，运行状态控制，寄存器/内存读写，断点设置等系列功能。

l  LLDB Server：与被调试程序进行交互的主体，通过调用debug api实现功能。

 

由于LLDB本身的功能实现需要周边多个组件的协同，包括：编译器，CANN运行时，昇腾芯片，昇腾驱动。为了保证其自身的独立性，需要满足如下原则：

−     针对编译器，仅需要保证其-g与无-g程序行为一致。保证不对CANN软件栈有任何特别的依赖。

−     针对调试器，保持自身的通用性，不能强依赖CANN软件栈。比如：默认设置CANN/编译器中特定函数作为私有断点等。代码中对下发可以做劫持。

−     针对RTS，特别是host侧的运行时，不需要感知debug模式。且本身提供CPU下ptrace中的类似行为，使得调试器操作行为逻辑一致。

−     针对驱动，仅提供host和device的进程间的通道，不感知和维护调试的状态信息。

−     针对芯片，选用的机制在现有主流芯片以及后续芯片上都能生效。

 

## 4.3 调试器（msdebug）功能域规格设计

 

![img](../pic/d46e51dad46e5c519ac2abc41e1a4917_667x350.jpg@900-0-90-f.jpg)

图3‑2 调试器(LLDB)适配昇腾的关键组件示意图

针对调试器，如上图所示，为了支持昇腾芯片，我们在原有调试器的基础上，对符号解析、进程处理等模块进行增强，同时，通过驱动，与昇腾芯片的RTS建立通道。该通道需要支持Host和device的信息交互。

 

## 4.4 调试器（msdebug）功能实现设计

### 4.4.1 调试使能功能实现

#### 4.4.1.1 功能概述

名称：调试使能

描述：msdebug支持拉起应用程序，现在支持多种不同的应用程序，比如：pytorch单算子

输入：

1. 用户使能断点

2. 算子应用程序由-O0 -g编译

输出：msdebug接管了应用程序控制权，并将断点等信息通过调试通道传到TS侧，并成功使能断点。

处理：msdebug拉起算子应用后，依据输入的断点信息，在kernel launch时，需要将断点信息通过调试通道使能。

规格：
1. 暂仅支持launch模式

2. 支持pytorch单算子模式和main函数混编模式

约束：NA

测试等级：必测

归属：自有

状态：正常

#### 4.4.1.2 增量SR清单

| **系统需求编号** | **系统需求**          | **系统需求描述**                                             |
| ---------------- | --------------------- | ------------------------------------------------------------ |
| XXX              | msdebug兼容驱动的变更 | 背景：  <br/>现客户现场发生硬件异常时，为了能定位该类问题，需要反复要求客户现场集群进行压测复现问题。用户体验差和问题定位效率低。   <br/>需求：  <br/>1. 调试的ko后续版本中将默认安装，并提供外部开关是否使能调试通道，资料刷新   <br/>2. 调试器同步验证相关特性是否受到干扰  <br/>验收方法：   <br/>1. 使用msdebug拉起算子应用，在调试通道开启下，能正常使用。   <br/>2. 使用msdebug拉起算子应用，在调试通道关闭下，能报错并告知原因。 |

#### 4.4.1.3 实现思路

对于调试器的使用，主要有2个差异性场景：1、应用程序在昇腾芯片上运行，支持对该过程的调试；2、遇到coredump后，使用调试器加载coredump，实现对coredump发生时的场景复现。

在板调试使能

在任何算子的使能方式中，其本质都是调用CANN的runtime实现kernel launch。对于调试使能而言，仅需要感知kernel launch，并利用该过程的数据与周边数据关联匹配，从而实现第一个断点的使能。

整体而言，有2个方案：

1、调试器劫持过程的大量接口（因为不同的使用场景的接口组合不一样，同类型接口可能存在多个）

2、将调试接口内置到RTS中，主要依赖2个关键点：

  a. RTS自身提供信息获取接口，支持在kernel launch阶段获取：PC地址，device Id， kernel名称（可以由kernel与加载地址存储接口获取）

  b. RTS的kernel launch调用链中触发某个特定函数A(本身仅包含RTS自身能力)，该A函数支持dl系列函数。调试阶段通过替换该函数A，实现调试能力注入。

coredump使能

通过加载coredump文件，实现对该异常场景的复现，并支持信息的查询等功能。

#### 4.4.1.4 实现设计

##### 4.4.1.4.1 支持上板调试使能

实现思路里的方案1相比方案2，能减少runtime下发任务的耗时。

方案1 实现如下

1. 调试器实现preload.so，劫持runtime接口

2. 劫持kernel launch接口后，需要获取相关start pc等信息设置断点下发

3. msdebug收到ts遇到断点后上报的信息

4. msdebug用户在命令行开始调试，如查询寄存器、内存等信息

图4-1 msdebug使能

![img](../pic/82b62396fcf30985af01addf3eac0209_655x630.gif@900-0-90-f.gif)

上板使能与coredump使能场景的区别：

1. 前者需要拉起用户进程，并且要preload调试的动态库

2. 前者工具需要与ts、用户进程通信交互

3. 工具内部使用的Process实例不同，见图2

图4-2 上板使能场景Process实例创建流程区别

![img](../pic/4e07edfd77540e9de6f82a143814d40a_663x336.gif@900-0-90-f.gif)

##### 4.4.1.4.2 支持coredump使能

参考友商使能coredump命令：

(cuda-gdb) target cudacore core.file

通过命令入参输入区分上板使能与coredump使能，后者命令行如下：

msdebug --core core.file

或

(msdebug) target create --core core.file

使能流程如图1

图4-3 corefile使能流程图

![img](../pic/7933b23b862d6c1581ac7954f8c830f2_659x436.gif@900-0-90-f.gif)

1. 用户使用--core参数加载coredump file

2. 命令行识别到存在coredump file后，需通过识别core file ELF header结构，会创建cpu 上的ProcessElfCore实例，还是npu上的ProcessElfCore实例

后续ProcessElfCore自身会对coredump file进行解析加载，恢复进程现场

coredump使能的流程在创建ProcessElfCore实例成功后即结束。后续基于ProcessElfCore实例加载coredump file以及读写数据不在本需求范围内。

#### 4.4.1.5 接口设计

上板使能

调试使能接口需要与RTS协同，在方案1下，遵从RTS本身的接口定义。在方案2下，用于接口的流程接口也由RTS确认。

Coredump使能

示例

msdebug --core core.file

或启动msdebug后

(msdebug) target create --core core.file

表4-1  

| **参数** | **类型** | **含义**          |
| -------- | -------- | ----------------- |
| core     | string   | core file文件路径 |

#### 4.4.1.6 DFX分析

##### 4.4.1.6.1 可靠性分析

4.4.1.6.1.1 FMEA分析

##### 4.4.1.6.2 可服务性分析

##### 4.4.1.6.3 安全设计检查

调试器拉起进程过程不能出现因调试通道未开启而导致的coredump等安全问题

4.4.1.6.3.1 安全设计确认

4.4.1.6.3.2 敏感操作检查

##### 4.4.1.6.4 可用性/性能分析

coredump使能场景功能可用性分析：

1. 需禁用断点设置、继续运行、单步运行等功能，并合理提示错误。

2. 变量打印、寄存器/内存打印正常使用。

3. core info查询只需显示当前有哪些核, pc地址，状态信息，方便切核查看上下文。

4. 调试信息的加载与上板原始逻辑保持一致，可从fatbin、so、环境变量动态导入

#### 4.4.1.7 分配需求

| **系统需求编号** | **系统需求**          | **分配需求编号** | **分配需求**                         | **分配需求描述**                                             | **系统元素**    |
| ---------------- | --------------------- | ---------------- | ------------------------------------ | ------------------------------------------------------------ | --------------- |
| XXX              | msdebug兼容驱动的变更 | XXX              | msdebug支持新的驱动使能方式（含资料） | 背景：  <br/>现客户现场发生硬件异常时，为了能定位该类问题，需要反复要求客户现场集群进行压测复现问题。用户体验差和问题定位效率低。   <br/>需求：   <br/>1. 调试的ko后续版本中将默认安装，并提供外部开关是否使能调试通道，资料刷新   <br/>2. 调试器同步验证相关特性是否受到干扰   <br/>验收方法：   <br/>1. 使用msdebug拉起算子应用，在调试通道开启下，能正常使用。   <br/>2. 使用msdebug拉起算子应用，在调试通道关闭下，能报错并告知原因。 | 调试器（msdebug） |

### 4.4.2 coredump加载功能实现

#### 4.4.2.1 功能概述

名称：coredump加载

描述：coredump是定位现网挂死问题的一个关键能力。调试器通过支持coredump的信息加载，在信息加载后，后续的查询类命令都基于加载的数据进行展示，实现在任何场景下无需复现就可以分析问题场景，避免了重复复现环境的难题。

输入：coredump文件

输出：调试器支持内存或者寄存器信息的查询

处理：
1. 调试器加载coredump文件，能顺利解析其中的各种数据的内容

2. 调试器使用查询类接口时，能顺利对接到coredump解析出来的文件，并正常展示

规格：

约束：
1. 对于coredump不包含的数据和数据范围，需要正常提示。

设计责任人：

测试等级：必测

归属：自有

状态：正常

#### 4.4.2.2 增量SR清单

| **系统需求编号** | **系统需求**            | **系统需求描述**                                             |
| ---------------- | ----------------------- | ------------------------------------------------------------ |
| XXX              | 支持A2/A3的coredump解析 | 背景：   <br/>随着产品发货的增多，硬件问题出现后，难以进行异常定位。现网发生算子执行异常时（AICore Error），运行时会将算子异常状态下的stack数据，icache数据，片上内存数据记录到bbox中，然后由定位人员依据相关信息结合kernel分析异常发生原因。由于数据收集不齐，所以需要不断地修改TS代码，然后进行压测。为了减少定位的压测次数，实现类似coredump能力，保证一次压测过程能将所有需要数据获取到，降低硬件异常等疑难问题的定位耗时。   <br/>需求：   <br/>由于现有方案针对特定数据进行解析，缺乏kernel与这些数据间的直接交互，需耗费大量时间进行分析处理。为了更好地将aicore  error场景复现，参考业内成熟的coredump机制，在运行时中生成coredump，然后，在调试器中加载，结合本身调试器提供的指令，辅助分析。也可以类似友商提供的coredump view的工具，对coredump数据进行分析   <br/>性能描述：无   <br/>约束：NA   <br/>DFX需求：无   <br/>验收标准：  不验收，仅分析coredump的文件格式，并在运行时检测到程序异常时，产生coredump，并支持在msdebug中加载使用。 |

#### 4.4.2.3 实现思路

针对coredump文件的识别，通过ELF文件的头识别并校验数据的合法性。当合法性满足要求后，将coredump数据的信息记录到工具中，便于后续查询接口使用。该特性仅针对加载阶段，此时最好记录数据范围等信息，便于查询时快速判断数据的整体有效性。

对于内部的数据存在如下差异：

1、栈信息：由于栈位置本身是一个逻辑概念，建议单独处理

2、全局数据：普通内存数据

3、片上内存：相对内存数据，需要添加核的标识，不过该标识也可以放到table上进行区分，而本身内部可以是UB，L0, L1等平铺。

4、寄存器：不同于内存数据格式，需要支持类似kv的内容存储。

#### 4.4.2.4 实现设计

##### 4.4.2.4.1 全局信息解析

cpu架构上，通常的ELF文件段示例如下：

![img](../pic/b75aeecb46ecd6c70cc283ba8a7060b6_426x473.gif@900-0-90-f.gif)

1. ELF header用户来识别这个文件类型信息，比如在什么机器架构上执行，是哪种类别的ELF

2. .text, .data等是存放对应数据的段，比如代码指段，数据段等

参考友商coredump file结构：

图4-4  

![img](../pic/15fb1a55f8d503038229a41c50942324_296x643.gif@900-0-90-f.gif)

基于上述结构，我们可以对npu device上的coredump file定义类似的结构：

coredump file文件整体结构如图1所示，新增.ascend.xxx段等5个Section，

图4-5  

![img](../pic/9f82c5c25dedabe6a2363e3d0c26a554_296x643.gif@900-0-90-f.gif)

如下为新增段的简要介绍

表4-2  

| **段名**       | **简要含义**                                                 |
| -------------- | ------------------------------------------------------------ |
| ELF header     | 其中应包含能识别是否npu device架构的信息                     |
| .ascend.devtbl | 全局设备信息，考虑到不同架构上的寄存器，内存类型可能不同，这里需要保存当时的设备类型，用到哪些ai core等信息 |
| .ascend.global | 用于记录kernel 在gm上占用的内存信息                          |
| .ascend.local  | 用于记录每个ai core在local memory的内容                      |
| .ascend.regs   | 用于记录每个ai core拥有的寄存器的值，                        |
| .ascend.bts    | 用于记录每个ai core调用栈信息，暂不分析                      |

下面对ELF header和.ascend.devtbl段信息做介绍：

*标准ELF header* 结构如下：

```c++
#define EI_NIDENT 16

typedef struct {
  unsigned char e_ident[EI_NIDENT];
  Elf32_Half e_type;
  Elf32_Half e_machine;
  Elf32_Word e_version;
  Elf32_Addr e_entry;
  Elf32_Off e_phoff;
  Elf32_Off e_shoff;
  Elf32_Word e_flags;
  Elf32_Half e_ehsize;
  Elf32_Half e_phentsize;
  Elf32_Half e_phnum;
  Elf32_Half e_shentsize;
  Elf32_Half e_shnum;
  Elf32_Half e_shstrndx;
} Elf32_Ehdr;
```

对于npu core file其中必须要的字段如表2所示，整体core file header 与标准ELF header格式保持一致即可

表4-3  

| **字段**    | **类型**   | **含义**                                                     |
| ----------- | ---------- | ------------------------------------------------------------ |
| e_shoff     | Elf64_Off  | 此字段指明节头表(section header table)开始处在文件中的偏移量。 |
| e_phnum     | Elf64_Half | 此字段表明程序头表中总共有多少个表项。                       |
| e_shentsize | Elf64_Half | 此字段表明在节头表中每一个表项的大小，以字节为单位。         |
| e_shstrndx  | Elf64_Half | 节头表中与节名字表相对应的表项的索引。                       |
| e_machine   | Elf64_Half | 表示体系结构体，npu上应该为0x1029。  通过识别ELF头信息里的e_machine字段来区分出corefile是host侧还是device侧 |
| e_type      | Elf64_Half | 表面该ELF文件为core文件类型                                  |

对于各个section而言，工具只会解析section里的内容，所以只需知道section名字和起始位置和大小即可，整体根据标准ELF section结构保持一致。

.ascend.devtbl

基于coredump场景如下功能考虑：

1.    不同npu设备上的寄存器列表不一样，内存类型、范围也可能不一

2.    不同kernel 运行时使用的aic core, aiv core数量等不一样

3.    友商coredump file里device table段里包含devType, numSMs, numWarpsPerSM等信息

4.    考虑以后可能同个类型核超过64个，需要多个bitmap

所以.ascend.devtbl段内信息如下：

表4-4  

| **字段**   | **类型**          | **含义**                                                     |
| ---------- | ----------------- | ------------------------------------------------------------ |
| dev_id     | uint32_t          | npu device id                                                |
| dev_type   | DevType(uint32_t) | 表示设备类型，比如A2/A3/310P等，用于区分该用哪一套寄存器表，以及区分下面aix_bitmap前面多少个bit表示aiv |
| version    | uint32_t          | core file版本号，方便后续做兼容                              |
| num_core   | uint32_t          | ai core的总个数，ceil(num_core/32) 对应aix_bitmap的数组长度  |
| aix_bitmap | uint32_t[0]       | 可变数组，当前kernel用了哪些ai core，bit位置1表示用了        |

##### 4.4.2.4.2 内存/寄存器信息解析

内存/寄存器的信息用于后续命令查询使用。涉及段如下

| **段名**       | **简要含义**                            |
| -------------- | --------------------------------------- |
| .ascend.global | 用于记录kernel 在gm上占用的内存信息     |
| .ascend.local  | 用于记录每个ai core在local memory的内容 |
| .ascend.regs   | 用于记录每个ai core拥有的寄存器的值，   |
| .ascend.bts    | 用于记录每个ai core调用栈信息，暂不分析 |

内存信息解析

.ascend.global段

基于如下考虑：

1.    kernel占用的gm内存可能是不连续的

2.    将来可能调试时需要拿到kernel的输入等信息

所以该段由多个GlobalMemInfo组成，每个GlobalMemInfo结构体见表4-5

工具加载时需要.ascend.global段进行解析，将多个global内存按起始地址排序好后列表存储，方便后续查询接口根据addr返回数据内容。

表4-5  

| **字段** | **类型**             | **含义**                            |
| -------- | -------------------- | ----------------------------------- |
| usage    | UsageType (uint32_t) | 记录这片gm内存的用途，具体见表4-6   |
| addr     | uint64_t             | 占用的gm内存的起始虚拟地址          |
| size     | uint64_t             | 占用的gm内存的大小，即content的大小 |
| content  | uint8_t[0]           | 可变长数组，存储gm内容              |

表4-6  

| **枚举类型**       | **值** | **含义**                               |
| ------------------ | ------ | -------------------------------------- |
| ASCEND_TENSOR      | 0      | kernel输入，包含input/output/workspace |
| ASCEND_TILING      | 1      | kernel tiling data                     |
| ASCEND_STACK       | 2      | cube上调用栈相关信息                   |
| ASCEND_HOST_O      | 3      | host缓存的算子.o                       |
| ASCEND_DEVICE_TEXT | 4      | device上的代码段                       |

.ascend.local

对.ascend.local段，每一个core，全量解析数据，存储不同内存类型的数据，方便后续查询接口根据core_id, core_type, mem_type, addr返回数据内容。

基于如下考虑：

1.    每个ai core上有自己的内存，且拥有内存虚拟地址都是0开始，可以省略addr字段

2.    每个ai core上有多种不同类型的内存

3.    减少重复的数据，节约空间，比如core_id只需出现一次

设计如下结构，整个段由多个LocalMemInfo 实例组成。

```c
struct LocalMemInfo { 
  uint32_t core_id; 
  uint64_t total_size; 
  MemPiece mems[0]; 
 } 
 struct MemPiece { 
  uint8_t mem_type; 
  uint8_t reserve[3]; 
  uint64_t size 
  uint8_t content[0]; 
 };
```

表4-7  

| **字段**   | **类型**          | **含义**                                          |
| ---------- | ----------------- | ------------------------------------------------- |
| core_id    | uint32_t          | core id， 与ts下core_id概念相同                   |
| total_size | uint64_t          | 该core占用的内存总大小，即mems的总和              |
| mem_type   | MemType (uint8_t) | 内存类型，比如L0A, L0B, ICACHE, DCACHE等，见表4-8 |
| size       | uint64_t          | content大小                                       |
| content    | uint8_t[0]        | 可变长数组，存储内存/cache内容                    |

表4-8  

| **枚举类型** | **值** | **含义**          |
| ------------ | ------ | ----------------- |
| L0A          | 1      | L0A内存类型       |
| L0B          | 2      | L0B内存类型       |
| L0C          | 3      | L0C内存类型       |
| UB           | 4      | UB内存类型        |
| L1           | 5      | L1内存类型        |
| FB           | 6      | FB内存类型        |
| SCALAR_BUF   | 9      | scalar buffer类型 |
| DCACHE       | 10     | dcache缓存        |
| ICACHE       | 11     | icache指令缓存    |

寄存器信息解析

对.ascend.regs 段进行解析，全量读取解析后，根据全局npu设备信号信息，和上板场景下的寄存器数据结构相同格式存储

基于以下考虑：

1.    每个ai core有自己的独立寄存器

2.    aiv与aic的寄存器集合存在部分差别

所以该段由多个REG_Entry结构体组成，每个REG_Entry如下所示

表4-9  

| **字段**  | **类型**           | **含义**                                                     |
| --------- | ------------------ | ------------------------------------------------------------ |
| core_id   | uint32_t           | aic/aiv core id                                              |
| core_type | CoreType(uint32_t) | core类型，比如aiv,  aic，这里类型为uint32_t是考虑到C里枚举类型是uint32_t类型 |
| addr      | uint64_t           | 寄存器号，如GPR30对应30，PC对应64                            |
| value     | uint64_t           | 寄存器的值                                                   |

##### 4.4.2.4.3 辅助信息解析

.ascend.aux段

考虑到需要支持切核功能，所以需要展示哪些核id，以及coredump在哪些核。

所以在coredump时把下述信息保存

```c
struct AuxInfo { 
  uint32_t num_status; // 同种设备上，status数组大小应该是确定的 
  uint32_t num_core; // core_info的个数 
  CoreInfo core_info[0]; 
 }; 
 
 struct CoreInfo { 
  uint32_t core_id; // ai core 索引，根据设备信息，基于aic总数重新标aiv序号，比如id>=25为aiv 
  uint64_t status[0]; // 异常错误码，不同设备上这个异常错误类型的数量不一样 
 } 
```

#### 4.4.2.5 接口设计

.ascend.devtbl Section

```c
struct DevInfo { 
  uint32_t dev_id; 
  DevType dev_type;
  uint32_t num_core; 
  uint32_t aix_bitmap[0]; 
 }; 
 
 enum DevType { 
  A2 = 1, 
  ASCEND_310P = 2, 
 };

.ascend.global 

struct GlobalMemInfo { 
  UsageType usage; 
  uint64_t addr; 
  uint64_t size; 
  uint8_t content[0]; 
 }; 
 
 enum UsageType { 
  ASCEND_TENSOR = 0, // kernel输入，包含input/output/workspace 
  ASCEND_TILING = 1, // kernel tiling data 
  ASCEND_STACK = 2, // core上调用栈相关信息 
  ASCEND_HOST_O = 3, // host缓存的算子.o 
  ASCEND_DEVICE_TEXT = 4,// device上的代码段 
 }; 
```

.ascend.local 

由多个LocalMemInfo组成，每个LocalMemInfo由多个MemPiece组成

```c
struct LocalMemInfo { 
  uint32_t core_id; 
  uint64_t total_size; 
  MemPiece mems[0]; 
 }; 
 struct MemPiece { 
  uint8_t mem_type; 
  uint64_t size; 
  uint8_t content[0]; 
 }; 
 
 enum MEM_TYPE { 
  L0A = 1, 
  L0B = 2, 
  L0C = 3, 
  UB = 4, 
  L1 = 5, 
  FB = 6, 
  SCALAR_BUF = 9 
  DCACHE = 10, 
  ICACHE = 11 
 }
```

.ascend.regs

```c
struct RegInfo { 
  uint32_t core_id; // ai core 索引，根据设备信息，基于aic总数重新标aiv序号，比如id>=25为aiv 
  uint64_t addr; 
  uint64_t value; 
 };
```

.ascend.auxinfo

```c
struct AuxInfo { 
  uint32_t num_status; // 同种设备上，status数组大小应该是确定的 
  uint32_t num_core_info; // core_info的个数 
  CoreInfo core_info[0]; 
 }; 

 struct CoreInfo { 
  uint32_t core_id; // ai core 索引，根据设备信息，基于aic总数重新标aiv序号，比如id>=25为aiv 
  uint64_t status[0]; // 异常错误码，不同设备上这个异常错误类型的数量不一样 
 }
```

#### 4.4.2.6 DFX分析

##### 4.4.2.6.1 可靠性分析

4.4.2.6.1.1 FMEA分析

##### 4.4.2.6.2 可服务性分析

##### 4.4.2.6.3 安全设计检查

corefile文件安全校验检查

1. corefile文件内容基本会加载到host内存里，加载前先做下host内存预估，防止host机器oom

2. 软连接，文件权限等安全校验

4.4.2.6.3.1 安全设计确认

4.4.2.6.3.2 敏感操作检查

##### 4.4.2.6.4 可用性/性能分析

#### 4.4.2.7 功能规格设计

#### 4.4.2.8 分配需求

| **系统需求编号** | **系统需求**            | **分配需求编号** | **分配需求**               | **分配需求描述**                                             | **系统元素**    |
| ---------------- | ----------------------- | ---------------- | -------------------------- | ------------------------------------------------------------ | --------------- |
| XXX              | 支持A2/A3的coredump解析 | XXX              | 支持coredump的数据结构加载 | 背景：  <br/>随着产品发货的增多，硬件问题出现后，难以进行异常定位。现网发生算子执行异常时（AICore Error)，运行时会将算子异常状态下的stack数据，icache数据，片上内存数据记录到bbox中，然后由定位人员依据相关信息结合kernel分析异常发生原因。由于数据收集不齐，所以需要不断地修改TS代码，然后进行压测。为了减少定位的压测次数，实现类似coredump能力，保证一次压测过程能将所有需要数据获取到，降低硬件异常等疑难问题的定位耗时。  <br/>需求：  <br/>由于现有方案针对特定数据进行解析，缺乏kernel与这些数据间的直接交互，需耗费大量时间进行分析处理。为了更好地将aicore  error场景复现，参考业内成熟的coredump机制，在运行时中生成coredump，然后，在调试器中加载，结合本身调试器提供的指令，辅助分析。也可以类似友商提供的coredump view的工具，对coredump数据进行分析  <br/>性能描述：无  <br/>约束：NA  <br/>DFX需求：无  <br/>验收标准：  不验收，仅分析coredump的文件格式，并在运行时检测到程序异常时，产生coredump，并支持在msdebug中加载使用。 | 调试器(msdebug) |

 

### 4.4.3 内存/寄存器读写功能实现

#### 4.4.3.1 功能概述

名称：内存/寄存器读写

描述：调试器支持内存读写

输入：调试器上的x命令（含内存类型，内存偏移和读取长度）

输出：内存上的信息内容

处理：调试器通过维测接口，在tscpu上通过debug bus读取片上内存信息，并将对应信息搬出。

规格：支持有效地址的内存/寄存器读

约束：

资产责任人：

设计责任人：

测试等级：必测

归属：自有

状态：正常

#### 4.4.3.2 增量SR清单

| **系统需求编号** | **系统需求**                      | **系统需求描述**                                             |
| ---------------- | --------------------------------- | ------------------------------------------------------------ |
| XXX              | 支持coredump的内存/寄存器信息查询 | 需求：  <br/>1. 基于coredump文件的加载数据，能通过msdebug的内存命令获取coredump的内存数据  <br/>2. 基于coredump文件的加载数据，能通过msdebug的寄存器命令获取coredump的寄存器数据  <br/>DFX：  <br/>1. 存在非法对象的信息查询，能正确报错说明不支持。  <br/>2. 存在非法范围的查询，能正确报错，说明不支持。  <br/>验证：  <br/>1. 加载coredump文件，能支持内存信息的查询。  <br/>2. 加载coredump文件，能支持寄存器信息的查询。 |

#### 4.4.3.3 实现思路

对于内存和寄存器的读写本身分为从coredump中读取，和直接从设备侧读写。

设备读写

针对设备侧的内存和寄存器的读写，本身在芯片内部都是对debug bus的读写。所以，对于msdebug而言，memory read和register read实际上对TS的要求一样。对于register read，需要与芯片内部的通用寄存器和特殊寄存器的名字完全一致。对于memory read，需要支持GM、UB、L0A、L0B、L0C上的内存读写。

对于GM的读写，需要注意存在cache，且由于芯片设计，我们芯片不保证cache一致性。首先查询cache上对应的地址的信息，如果不命中再读取GM上的数据。

coredump读

对于支持corefile后，如果加载了corefile，则需要内存和寄存器读命令支持展示corefile中的信息。

注意：对非法场景的拦截，包括：数据对象不存在，数据范围越界。

#### 4.4.3.4 实现设计

##### 4.4.3.4.1 寄存器读

![img](../pic/b5fb5732a6040f9573a5ce5ee1305f5d_660x244.gif@900-0-90-f.gif)

##### 4.4.3.4.2 基于coredump的内存/寄存器读

coredump场景与上板场景读内存/寄存器的命令行接口一致。

寄存器读

register read [REGISTER_ADDR|REGISTER_VALUE]

内存读

x -m [MEM_TYPE] [ADDR] [SIZE]

在corefile中，我们已经保存了内存和寄存器的信息。参考msdebug cpu架构上基于core file调试场景，代码上主要通过ProcessElfCore类。所以npu上可类似地直接从corefile里读取，鉴于npu corefile结构有其特殊性（比如有多种不同类型的内存，同种类型的内存可能离散存着多份），可以继承ProcessElfCore新设计一个ProcessElfCoreDevice类，实现相关读内存、写内存接口。

 

寄存器与内存读流程如[#ZH-CN_TOPIC_0000002175532785/fig121613153183](# )所示：

图4-6 寄存器读

![img](../pic/9863825d88298b8b626137de9add59c3_657x512.gif@900-0-90-f.gif)

读内存/寄存器的前置流程：

1. 使能coredump模式，运行时流程都在msdebug客户端完成

2. msdebug创建相应的ProcessElfCore实例

3. ProcessElfCore实例加载解析coredump文件，创建对应设备侧的RegisterContextCore_ascend实例并初始

读寄存器

1. 用户输入register read读寄存器命令

2. 命令行会获取到当前对应的RegisterContext并从解析好corefile的数据里拿到寄存器信息

读内存

1. 用户输入register read读寄存器命令

2. 命令行会获取到当前对应的RegisterContext并从解析好corefile的数据里拿到内存信息

#### 4.4.3.5 接口设计

命令行接口与上板调试场景保持一致

内部新增关键接口

```
ReadMemory(lldb::addr_t vm_addr, void *buf, size_t size, const ArchSpec &arch_spec, DeviceAddressClass address_class, Status &error)
```

该接口用于读取内存数据，由于可能多个相同类型的内存信息段，实现时需要在多个内存信息段中遍历寻找。该接口基本与上板读取内存保持一致，但是需放置在ProcessElfCore类，或者新增一个继承ProcessElfCore的子类里实现。

参考ProcessElfCore类，新增ProcessElfCoreDevice类对corefile解析后的数据进行最上层的封装管理。

入参说明

表4-10  

| **参数**      | **含义**                                        |
| ------------- | ----------------------------------------------- |
| vm_addr       | 读取的内存虚拟地址                              |
| buf           | 用于存储读取到的数据                            |
| size          | 读取的内存大小，单位字节                        |
| arch_spec     | 读取的设备信息，用于区分host/device上的内存读取 |
| address_class | 读取的内存类型，如UB, GM, L0等                  |
| error         | 读取失败时，设置的error信息                     |

```
ReadRegister(const RegisterInfo *reg_info, RegisterValue &value)
```

用于读取寄存器数据，该接口基本与上板读取寄存器接口保持一致，但是需新增RegisterContextCorePOSIX_ascend类，放在其中，该类用于辅助Process类管理寄存器上下文；具体可参考RegisterContextCorePOSIX_arm类。

入参说明

表4-11  

| **参数** | **含义**                 |
| -------- | ------------------------ |
| reg_info | 包含寄存器号，名字等信息 |
| value    | 寄存器的值，出参         |

#### 4.4.3.6 DFX分析

##### 4.4.3.6.1 可靠性分析

4.4.3.6.1.1 FMEA分析

##### 4.4.3.6.2 可服务性分析

##### 4.4.3.6.3 安全设计检查

1. 读取不在coredump文件里记录的寄存器时，根据当前寄存器在该device上是否应该存在，打印对应合理的提示

2. 读取内存范围越界时，打印合理的提示，防止越界行为发生

4.4.3.6.3.1 安全设计确认

4.4.3.6.3.2 敏感操作检查

##### 4.4.3.6.4 可用性/性能分析

#### 4.4.3.7 分配需求

| **系统需求编号** | **系统需求**                      | **分配需求编号** | **分配需求**                        | **分配需求描述**                                             | **系统元素**    |
| ---------------- | --------------------------------- | ---------------- | ----------------------------------- | ------------------------------------------------------------ | --------------- |
| XXX              | 支持coredump的内存/寄存器信息查询 | XXX              | 支持coredump中的内存/寄存器信息获取 | 需求：  <br/>1. 基于coredump文件的加载数据，能通过msdebug的内存命令获取coredump的内存数据  <br/>2. 基于coredump文件的加载数据，能通过msdebug的寄存器命令获取coredump的寄存器数据  <br/>DFX：  <br/>1. 存在非法对象的信息查询，能正确报错说明不支持。  <br/>2. 存在非法范围的查询，能正确报错，说明不支持。  <br/>验证：  <br/>1. 加载coredump文件，能支持内存信息的查询。  <br/>2. 加载coredump文件，能支持寄存器信息的查询。 | 调试器(msdebug) |

### 4.4.4 需求分解分配表

| **功能编号** | **功能名称**      | **系统需求编号** | **系统需求**                      | **分配需求编号** | **分配需求**                         | **分配需求描述**                                             | **系统元素**    |
| ------------ | ----------------- | ---------------- | --------------------------------- | ---------------- | ------------------------------------ | ------------------------------------------------------------ | --------------- |
| XXX          | 调试器（msdebug） | XXX              | 支持A2/A3的coredump解析           | XXX              | 支持coredump的数据结构加载           | 背景：  <br/>随着产品发货的增多，硬件问题出现后，难以进行异常定位。现网发生算子执行异常时（AICore Error），运行时会将算子异常状态下的stack数据，icache数据，片上内存数据记录到bbox中，然后由定位人员依据相关信息结合kernel分析异常发生原因。由于数据收集不齐，所以需要不断地修改TS代码，然后进行压测。为了减少定位的压测次数，实现类似coredump能力，保证一次压测过程能将所有需要数据获取到，降低硬件异常等疑难问题的定位耗时。  <br/>需求：  <br/>由于现有方案针对特定数据进行解析，缺乏kernel与这些数据间的直接交互，需耗费大量时间进行分析处理。为了更好地将aicore  error场景复现，参考业内成熟的coredump机制，在运行时中生成coredump，然后，在调试器中加载，结合本身调试器提供的指令，辅助分析。也可以类似友商提供的coredump view的工具，对coredump数据进行分析  <br/>性能描述：无  <br/>约束：NA  <br/>DFX需求：无  <br/>验收标准：  不验收，仅分析coredump的文件格式，并在运行时检测到程序异常时，产生coredump，并支持在msdebug中加载使用。 | 调试器(msdebug) |
| XXX          | 调试器（msdebug） | XXX              | msdebug兼容驱动的变更             | XXX              | msdebug支持新的驱动使能方式（含资料） | 背景：  <br/>现客户现场发生硬件异常时，为了能定位该类问题，需要反复要求客户现场集群进行压测复现问题。用户体验差和问题定位效率低。  <br/>需求：  <br/>1. 调试的ko后续版本中将默认安装，并提供外部开关是否使能调试通道，资料刷新  <br/>2. 调试器同步验证相关特性是否受到干扰  <br/>验收方法：  <br/>1. 使用msdebug拉起算子应用，在调试通道开启下，能正常使用。  <br/>2. 使用msdebug拉起算子应用，在调试通道关闭下，能报错并告知原因。 | 调试器(msdebug) |
| XXX          | 调试器（msdebug） | XXX              | 支持coredump的内存/寄存器信息查询 | XXX              | 支持coredump中的内存/寄存器信息获取  | 需求：  <br/>1. 基于coredump文件的加载数据，能通过msdebug的内存命令获取coredump的内存数据  <br/>2. 基于coredump文件的加载数据，能通过msdebug的寄存器命令获取coredump的寄存器数据  <br/>DFX：  <br/>1. 存在非法对象的信息查询，能正确报错说明不支持。  <br/>2. 存在非法范围的查询，能正确报错，说明不支持。  <br/>验证：  <br/>1. 加载coredump文件，能支持内存信息的查询。  <br/>2. 加载coredump文件，能支持寄存器信息的查询。 | 调试器(msdebug) |

 
