# **step-2_4 精度问题：msdebug定位SetValue问题**

## 1. 运行脚本

sh run.sh 8 8
现象：
算子功能正常，但精度异常；并且相同数据，运行多次，程序输出结果不同，表现为随机性；

![image-20251212113823635](../../pic/b94a294a17875d0f53458180c82f68a0_1417x203.png)

但mssanitizer未检测到同步问题；



## 2. msdebug单步调试和变量打印排查问题

先打印标杆数据loss，具体如下：

![image-20251212104848723](../../pic/352c9783b1b626844dba424b96e4d49a_1081x25.png)

断点设置在118行，先排查每个batch的loss计算是否正确；
progress = 0时loss计算正确；

![image-20251212104920410](../../pic/1c85c064ec4ef77909f23015f60e1080_2036x407.png)

![image-20251212104931361](../../pic/94857fcb7dfa7772942b096a23722a97_1201x640.png)

使用continue命令调试下一个progress，continue命令的行为：c

![image-20251212105000956](../../pic/eaa0009a4d615810fe37c05e49832de3_2049x554.png)

排查后发现0核所有progress计算均正确；

![image-20251212105015862](../../pic/c7b30f853ce1052d2b758fb5b21d2d7c_1955x443.png)

使用ascend info cores查看算子运行的其他核；

![image-20251212105031546](../../pic/4eca37187c66ba9a496005fa116a6929_1096x127.png)

使用ascend aiv 14切换到block 1查看loss计算情况，发现1核的所有progress计算均正确；

![image-20251212105100608](../../pic/e64fc3a4f9ff0a8bac57cd2ad1a6a628_1773x1024.png)

重新运行算子(r)，并断点设置在130行，定位根因：

![image-20251212105131976](../../pic/2550664264d246b70795cc1d90767a8e_1880x413.png)

![image-20251212105156846](../../pic/ce35641e05713d5d2804a387cc3ae5ff_1819x693.png)

发现lossBufferGm 0核和1核写入正确，但执行到130行时，lossBufferGm上0核写入的数据（前4个数据丢失），进而导致了精度问题；
查阅ascendc官方文档关于SetValue的介绍，发现多核通过SetValue往GM写入时，多核之间偏移需要大于64B，否则会出现数据随机覆盖问题，算子表现为精度多次运行结果不一致；

![image-20251212105213010](../../pic/3f60a8dda506fcab8887dd5d3ce88ef9_1010x790.png)



## 3. 修复多核偏移问题

![image-20251212105232415](../../pic/b625cf19f2032f2ba949babc6ff5e559_1132x1032.png)
