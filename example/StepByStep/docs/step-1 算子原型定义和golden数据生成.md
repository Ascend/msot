# **step-1 算子原型定义和golden数据生成**

## 1. 算子原型

![image-20251212103021935](../../pic/185dc931ef3a8ca357ec6d8b82f6511e_948x569.png)

## 2. 计算逻辑

![image-20251212103059691](../../pic/c42a1833e15e13786defc18578041cb6_1273x875.png)

## 3. 标杆数据生成

借助torch基础API，实现标杆数据的生成

![image-20251212103122902](../../pic/abf4b63e3ff60463155d8877f3a88ff6_797x287.png)

## 4. 算子设计方案

算子需要固定对N个元素求ReduceSum，目前算子并行策略为按照batch维度，每个核均分batch；
算子内部buffer划分如下：

1. 由于需要缓存ReduceSum的结果，UB上需要4个字节的缓存空间；
2. 由于需要缓存算子的onehot结果，UB上需要 N * sizeof(int32_t)的缓存空间；
3. 由于需要缓存cast之后的onehot结果，UB上需要 N * sizeof(float)的缓存空间；

故算子内部需要的buffer总大小为：4 + N * sizeof(int32_t) + N * sizeof(float);

初版算子tiling设计如下：
包含3个维度；batch_size，num_class以及算子blockDim



## 5. 算子代码实现

略



## 6. 代码运行

sh run.sh batch_size num_class
第一个入参为batch_size，第二个入参为num_class；