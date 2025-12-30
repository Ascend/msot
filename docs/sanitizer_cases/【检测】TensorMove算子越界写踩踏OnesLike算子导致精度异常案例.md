# **【检测】TensorMove算子越界写踩踏OnesLike算子导致精度异常案例**

## 一、问题讨论

1. 算子越界写的根因是什么？
2. 什么情况下的越界写会导致精度问题，什么情况下的越界写不会导致精度问题？
3. 越界写的标准是比较算子的真实shape还是PTA分配的内存？



## 二、问题背景

**问题描述**：输入shape为[2, 11, 51866]，tensor_copy之后**torch.ones**算子出现**精度问题**。copy之后torch.ones的[1][0][:20]的**前两个元素**精度出现异常，前两个元素正确的结果应为[1,1]。并且将
npu_select_tmp.copy_(npu_slice_grad)**注释掉**之后，精度**正常**，怀疑copy底层算子越界踩踏了onesLike算子导致了精度异常。

![image-20251212112949310](../pic/becd3b1ef21d24f62271f2dbd836da75_1539x377.png)

多算子脚本如下：

```python
import torch,torch_npu
torch.manual_seed(100)
torch.npu.set_device(1)
torch.npu.set_compile_mode(jit_compile = False)
input = torch.randn(2, 11, 51866).npu()
input_cpu = torch.clone(input).cpu()
npu_sel = input.select(0, 0)
res_npu = torch.ops.aten.slice(npu_sel, 0, 3, 11, 1)
grad_input = torch.ones_like(res_npu)                                                                                               
npu_slice_grad = torch.ops.aten.slice_backward(grad_input, [11, 51866], 0, 3, 11, 1)                             
npu_grad_input = torch.ones(size = [2, 11, 51866], dtype = torch.float32, device = "npu")
npu_select_tmp = npu_grad_input.select(0, 0)
print("======== after select but before copy ==========")
print('npu_grad_input_1_0_20', npu_grad_input[1][0][:20])
npu_select_tmp.copy_(npu_slice_grad)
print("===================================================== after copy ===========================================================")
print('npu_grad_input_1_0_20', npu_grad_input[1][0][:20])
res_all = torch.add(npu_grad_input, input)
```





## 三、定位思路

1): 使用内存检测工具启动上述python脚本，检测其中算子越界问题

![image-20251212113024687](../pic/3d387875efe393ed7285b3be208e95b8_1656x730.png)



## 四、定位步骤

**1、检测工具生成异常内存记录共4条**

其中第159行发生GM上的越界读问题，162行发生GM上的越界写问题
具体CCE文件如下：

![image-20251212102732835](../pic/342ec0825fb02b6e3ee91113fd58b874_1787x130.png)

**2、 分析过程**
TensorMove算子在1971芯片上底层搬运指令未使用pad逐字节搬运指令，该网络中TensorMove shape为[11, 51866]，dtype:float32，总搬运大小：**2282104**字节，**尾块**搬运时，向上对齐**32字节**之后，多搬运**8字节**，导致了**越界写**了8个字节。
整个网络运行中，内存布局图如下图所示：
网络中包含两个TensorMove算子，均有越界写问题。由于TensorMove_2算子和OnesLike_2算子共用起始地址，TensorMove_2算子越界之后，踩踏了OnesLike算子的中间**8个字节**数据，导致了OnesLike算子的**精度异常**。

![image-20251212102804715](../pic/26f5593fa86854dcf522d26cfb84808c_2117x929.png)



## 五、总结

1. 算子越界写的根因是什么？
   算子越界写多为硬件搬运指令限制。搬运指令分为两种，dataCopy和dataCopyPad，前者搬运需32字节对齐，后者搬运指令可以逐字节搬运并且只支持1971芯片，并且数据类型为bool、float64、int64_t或uint64_t时，1971芯片并不支持。部分算子开发为了算子代码的通用性，统一使用dataCopy，遇到非对齐shape时，向上32字节对齐，产生内存越界写行为。

2. 什么情况下的越界写会导致精度问题？什么情况下的越界写不会导致精度问题？
   PTA分配的内存为512字节对齐，比如TensorMove_1实际占用内存大小为：4564208字节，PTA分配给该tensor的内存为：4564480字节。越界写对应的地址空间只有当前算子持有的，这部分越界写行为由于PTA框架的多分配情况，并不会导致精度问题。
   当越界写对应的算子地址空间和其他算子共用时，越界写行为会踩踏其他算子，导致其他算子精度异常。

3. 越界写的标准是比较算子的真实shape还是PTA分配的内存？
   基于第2点，越界写的标准应比较tensor的真实shape，而不是PTA多分配的内存。