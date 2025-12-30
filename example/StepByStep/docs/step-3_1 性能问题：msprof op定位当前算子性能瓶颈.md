# **step-3_1 性能问题：msprof op定位当前算子性能瓶颈**

## 1. 采集标杆性能数据

sh run.sh 128 1024
目前该样例只针对了特定shape做了性能优化，其他shape未做相关优化；
目前实现内部由3个小算子组成；
LogSoftmax + OnesLike + NLLLoss;
msprof性能指标为：7.1825 + 2.6125 + 7.57125 = 17.36625 us

![image-20251212105527770](../../pic/4a77a37538e49e03d7ab0a8a95a0cb5a_818x204.png)



## 2. 采集算子性能数据

先根据shape信息，做对比实验，验证最优的blockDim，以此作为baseLine；经实验，最优的blockDim为40；
msprof op ./run.fatbin 128 1024
其中耗时最多的为scalar操作；

![image-20251212105601638](../../pic/f5bdfd0c5d329242cdfdd5bf93674a96_2139x694.png)



## 3. 采集算子仿真流水图

msprof op simulator --soc-version=Ascend910B4 ./run.fatbin
通过仿真流水图查看，Vmuls和Vconv计算指令中间存在大量scalar计算，由此导致性能较差；

![image-20251212105629642](../../pic/02536c1c93d15bb0374d70a784b0295a_2133x929.png)

通过调用栈可定位到代码第112行；

![image-20251212114021587](../../pic/a91c23599486b536174d0441a4b72adf_1194x1033.png)



## 4. 优化scalar计算

通过上板和仿真，已经识别到当前算子由于将num_class进行One-Hot操作导致性能瓶颈，过程中存在大量scalar操作；
使用Duplicate 设置labelOneHostLocal_为0，并且最后只需要一次scalar设置labelIdx为1，代码片段如下：

![image-20251212105736241](../../pic/5c1be87fcb27a2cf010ed7e75f9a3d43_1381x477.png)

优化后的性能指标如下：
耗时由27.22提升到16.94，提升38%；

![image-20251212105752721](../../pic/5b7584b5c839a3c6a776dd9f1c219f50_2137x816.png)

优化之后的流水图如下：

![image-20251212105806817](../../pic/64770acccbf6171b6e56a68c6fc79ee7_2138x794.png)



## 5. 优化冗余计算

原先计算逻辑labelOneHostLocal_ 为int32_t类型，会先进行cast转换为float类型后和logitLocal做乘法运算；
可以优化为：
在SetValue时，直接往labelOneHostLocal_处写入float值，省去了cast运算；

![image-20251212105948750](../../pic/f94ca23306b3698220bfd64f4376e9e0_1338x449.png)

优化后的代码片段如下：

![image-20251212110002277](../../pic/1bf99c705509cc643679de4fdbac0084_1252x1027.png)

优化后的性能指标如下：
由16.94优化到14.04，提升17%；

![image-20251212110018580](../../pic/b5af04bae0ef5345b9bf589bb2421559_2113x716.png)



## 6. 优化冗余搬运链路

算子逻辑中关于label的搬运链路为：
GM->UB->Stack;
其中搬运到UB为冗余搬运，可以直接从GM->Stack;

![image-20251212110041036](../../pic/8fbd9eb1e176ae9202b1d307074b2eb2_1413x910.png)

优化后的代码片段如下：

![image-20251212110055477](../../pic/69d019e0ccb5ee95bb870881a43ecf5c_1230x1034.png)

优化后的性能指标如下：
由14.04优化到13.07，提升7%；

![image-20251212110112480](../../pic/071e555487bb5e2d50bdada310fcaaa0_2143x717.png)



## 7. 多余同步指令优化

同步指令中，当存在pipe-s的dst同步时，相当于对src的pipe有流水内同步的作用；
对应代码，则97行和107行为多余的同步指令，可以删除；

![image-20251212110132684](../../pic/147f2814cfd00005469943b5efa60587_1216x1026.png)

优化后的性能指标如下：
由13.07优化到11.32，提升13%；

![image-20251212110153725](../../pic/c26c8d4dfbc5a7adc263de176181e7a8_2136x826.png)



## 8. 移动计算逻辑消除冗余同步指令

代码逻辑如下：
93/93行和100/101行均为v->s的同步指令，并且labelOneHostLocal_和logitLocal并无UB数据依赖关系，故可以移动计算逻辑，消除多余的v->s以及s->v的同步指令；

![image-20251212110217187](../../pic/6cd5cc3a4a003d29501746c205eb5b56_1368x992.png)

优化后的代码逻辑如下：

![image-20251212110243988](../../pic/0434021f0a2d487baa4bac201fae089a_1271x847.png)

优化后流水图：

![image-20251212110303673](../../pic/7854dfc05cd420cd95d542aad3b05ad4_1525x1025.png)

发现上一轮尾部计算和下一轮搬入计算流水图之间存在较大间隙，查看调用栈中间存在较多scalar指令；
搬入阶段的logitMovBytes存在重复计算；

![image-20251212110319648](../../pic/66595bda1b7cebd99c68c17fe253f03d_1635x273.png)

优化后的性能指标如下：
由13.07优化到11.32，提升13%；





