# **step-2_3 精度问题：mssanitizer定位算子同步问题**

## 1. 运行脚本

sh run.sh 8 8
现象：
算子功能正常，但精度异常；并且相同数据，运行多次，程序输出结果不同，表现为随机性；

![image-20251212113635896](../../pic/6f60bd7299a1918cfff6dcabc18bc62b_1382x362.png)

## 2. mssanitizer排查同步问题

多数偶发问题为同步问题，使用mssanitizer racecheck功能检测同步问题；
mssanitizer -t racecheck ./run.fatbin 8 8
工具提示多处同步问题，

![image-20251212104625636](../../pic/f12e76222fe9578690d83f0d03a03052_1951x370.png)

以上述为例，工具提示第 116 行发生在 PIPE_MTE2 上，第 117 行发生在 PIPE_V 上。两条 pipe 之间存在数据依赖，但缺少同步指令，导致竞争错误。根据报错信息，在相应的 pipe 前插入同步指令即可消除同步问题。

![image-20251212104700083](../../pic/fa8e72886a2cefd92bcc34e107186bcf_1968x338.png)

## 3. 修复同步问题 

![image-20251212104722229](../../pic/972fecd0101d276466113de952c6b69f_1130x1033.png)



