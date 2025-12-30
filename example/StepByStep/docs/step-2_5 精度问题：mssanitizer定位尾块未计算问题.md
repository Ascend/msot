# **step-2_5 精度问题：mssanitizer定位尾块未计算问题**

## 1. 运行脚本

sh run.sh 8 8
现象：
算子精度异常，切换shape为[7, 8]后精度异常。

![image-20251212113937904](../../pic/1d3aa39ab0d725ad92ee4c1ca8c90cf8_1669x690.png)

但mssanitizer未检测到同步问题；





















