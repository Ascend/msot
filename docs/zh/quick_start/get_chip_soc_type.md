# 昇腾芯片 SoC 型号获取方法

<br>

>[!NOTE]须知   
>**知识点（必读）：昇腾卡芯片 SoC 型号概念**   
>昇腾 A2/A3 代表产品代际：    
>A2：基于昇腾 910B 芯片的 AI 加速平台。       
>A3：基于昇腾 910C 芯片的 AI 加速平台。       
>不同型号的卡存在硬件差异，上层工具可通过"芯片 SoC 型号"（如 Ascend910B4）进行差异化处理。

## 1. 获取 NPU ID 和 Chip ID

执行如下命令：

```shell
npu-smi info -m
```

输出示例如下：

```text
[root@localhost ~]$ npu-smi info -m
        NPU ID                         Chip ID                        Chip Logic ID                  Chip Name                     
        0                              0                              0                              Ascend 910B4
        0                              1                              -                              Mcu                           
        1                              0                              1                              Ascend 910B4
        1                              1                              -                              Mcu         
```

一般认为一台服务器上所有芯片类型都相同，取第一行数据的 NPU ID 和 Chip ID 列的值即可（当然也可以使用您指定的值）。例如上面的输出中，NPU ID 为 0，Chip ID 为 0。

## 2. 根据 ID 获取 Chip Name

执行如下命令，-i 的值是上面获取的 NPU ID，-c 的值是上面获取的 Chip ID：

```shell
npu-smi info -t board -i 0 -c 0
```

A2 环境输出示例如下：

```text
[root@localhost ~]$ npu-smi info -t board -i 0 -c 0
        NPU ID                         : 0
        Chip ID                        : 0
        Chip Type                      : Ascend
        Chip Name                      : 910B4
```

A3 环境输出示例如下：

```text
[root@localhost ~]$ npu-smi info -t board -i 0 -c 0
        NPU ID                         : 0
        NPU Name                       : 9392
        Chip ID                        : 0
        Chip Name                      : Ascend910
```

对于 A2/A3 芯片：A2/A3 芯片都有 Chip Name；A3 有 NPU Name，A2 没有；A2 有 Chip Type，A3 没有。

## 3. 拼接最终芯片 SoC 型号

A2 芯片 SoC 型号公式为：`{Chip Type}{Chip Name}`，例如：Ascend910B4。   
A3 芯片 SoC 型号公式为：`{Chip Name}_{NPU Name}`，例如：Ascend910_9392。

按如上公式获得芯片 SoC 型号后，请记录好，后续步骤中需要使用。
