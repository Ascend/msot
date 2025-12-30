# **step-2_1 AicoreError问题：mssanitizer和msdebug定位aicore error问题**

## 1. 运行脚本

sh run.sh batch_size num_class
第一个入参为batch_size，第二个入参为num_class；

sh run.sh 8 8

![image-20251212103345738](../../pic/60ab7c753c376c04b7b813843af21787_1939x282.png)现象：
算子出现aicore error问题；



## 2. 原因分析

算子出现aicore error可能原因如下：

1. 地址对齐；
2. 地址越界；
3. 竞争问题；
4. api使用错误；

 mssanitizer工具支持地址对齐、地址越界、竞争分析，先用mssanitizer排查上述问题；



## 3. mssanitizer工具使用

内核调用场景，使用mssanitizer需要编译算子阶段加入-g --cce-enable-sanitizer，链接阶段需要加入--cce-enable-sanitizer；

![image-20251212103510151](../../pic/9e2865cae199fb3fbd014e058ab0866e_1488x777.png)

编译完成之后，使用工具启动算子编译的二进制文件；
mssanitizer ./run.fatbin 8 8

![image-20251212103549099](../../pic/44ba869dac4122e1ebbaaa60d351fc90_1899x595.png)

工具提示UB存在非对齐问题，非对齐地址发生在0和1核的算子代码92行，地址分别为0xac和0xa4，并非32字节对齐导致了算子崩溃问题；
92行代码如下：

![image-20251212103603791](../../pic/04dcaf5d60f217bd414a8b560591b25f_1197x35.png)

两处UB地址空间均为算子内部Tbuf划分，使用msdebug打断点和单步调试，进一步定位问题根因；



## 4. msdebug工具使用

算子编译阶段加入-g -O0；

![image-20251212103622280](../../pic/9ad1083ea106209cb993b4219094b7e5_1432x803.png)

断点打到代码30行；

![image-20251212103710510](../../pic/a673c1c949ecbd29db884782cac7acb7_1545x368.png)

使用步骤：

1. 编译算子时加入-g -O0
2. 使用msdebug启动算子脚本：msdebug ./run.fatbin 8 8
3. 设置断点，b cross_entropy.cpp:30
4. 运行算子，输入r

![image-20251212113226269](../../pic/8d71dd95d94d07335303c863f0eafd50_1871x585.png)

## 5. 使用单步调试（n）和变量打印（p）定位问题

![image-20251212103824637](../../pic/32af2c42750e3d35c2e2090036e67468_1779x349.png)

![image-20251212103837303](../../pic/9e3c1cf8866465fae2b2724323c89e14_1791x633.png)

打印labelOneHotLocal显示，该localTensor地址为164，非32字节对齐；
根本原因是Tbuf地址划分时，先划分了4个字节给reduceSumLocal，之后划分了32字节给labelOneHotLocal；划分时未按照32字节对齐导致了非对齐问题；

## 6. 修复非对齐问题

![image-20251212103936894](../../pic/e3c25d6c4204c277c6e55cfeb6002dcb_1519x360.png)

地址空间划分时，根据对齐函数按照32字节对齐分配和划分；