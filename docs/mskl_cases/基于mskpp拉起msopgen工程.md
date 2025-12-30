# 0.重要

wiki内容已经迁移至社区，最新内容以社区贴为准：[【热门功能介绍】基于msKPP拉起msOpGen工程](https://openx.huawei.com/communityHome/postDetail?postId=16069&id=296)
其他mskpp相关内容见社区贴：[【热门功能介绍】msKPP实现轻量化算子调用与Tiling调测](https://openx.huawei.com/communityHome/postDetail?postId=16197&id=296)

# 1.简介

演示如何为自定义算子编写一个用mskpp调用算子的python脚本。

文中涉及的ascendc代码来源于sample代码仓的算子，目录为samples-master/operator/ascendc/0_introduction/12_matmulleakyrelu_frameworklaunch。调用脚本也用于启动该算子。（第3步有工程文件）

使用的cann包最好是2025/7/9以及之后的，比如[CANN 8.3.RC1.B106-20250709023501](https://cmc-szv.clouddragon.huawei.com/cmcversion/index/findSnapshotRelease?deltaId=12928538960483584&isSelect=Software)，否则文中的部分功能可能会没有。

# 2.准备工作

安装cann toolkit和kernel包，mskpp本身仅依赖toolkit包。

调用算子tiling需要：

- 编写好tiling代码，编译出liboptiling.so（有些工程是libcust_opmaster_rt2.0.so）

调用算子kernel需要：

- 编写好kernel代码，编译出kernel.o
- 先调用算子tiling

# 3.生成工程

已有自己算子工程的情况，准备好tiling.so和kernel.o后，可跳过本步骤。

1. 解压压缩包并进入目录
   
   ```bash
   unzip matmulleakyrelu.zip
   cd matmulleakyrelu
   ```
2. 生成工程，生成时会删除当前目录下的CustomOp目录
   
   ```bash
   bash install.sh -v Ascend910B4
   ```
3. 进入工程目录
   
   ```bash
   cd CustomOp
   ```
4. 编译和部署算子
   
   ```bash
   bash build.sh
   # run包名称根据实际情况填写
   ./build_out/custom_xxx.run
   ```

# 4.编写脚本

一个py脚本通常可以分为4个部分，下面会详细描述每个部分如何填写，格式如下

```python
# region x.
...
# endregion x
```

代码样例如下：

```python
import numpy as np
import mskpp


# 该函数入参必须和kernel函数入参一致
def run_kernel(input_a, input_b, input_bias, output, workspace, tiling_data):
    kernel_binary_file = "./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/matmul_leakyrelu_custom/MatmulLeakyreluCustom_97ef75830e63ebe749e7c029d8d403c5.o"
    kernel = mskpp.get_kernel_from_binary(kernel_binary_file)
    return kernel(input_a, input_b, input_bias, output, workspace, tiling_data)


if __name__ == "__main__":
    # region 1.构造kernel入参
    M = 1024
    N = 640
    K = 256

    input_a = np.random.randint(1, 10, [M, K]).astype(np.float16)
    input_b = np.random.randint(1, 10, [K, N]).astype(np.float16)
    input_bias = np.random.randint(1, 10, [N]).astype(np.float32)
    output = np.zeros([M, N]).astype(np.float32)
    # endregion 1

    # region 2.调用算子tiling函数
    tiling_output = mskpp.tiling_func(
        op_type="MatmulLeakyreluCustom",
        inputs=[input_a, input_b, input_bias],
        outputs=[output],
    )
    blockdim = tiling_output.blockdim
    workspace_size = tiling_output.workspace_size
    tiling_key = tiling_output.tiling_key
    tiling_data = tiling_output.tiling_data # 以 numpy array类型返回
    workspace = tiling_output.workspace # 以 numpy array类型返回
    # endregion 2

	# region 3.调用算子kernel
    run_kernel(input_a, input_b, input_bias, output, workspace, tiling_data)
    # endregion 3

    # region 4.精度比较
    alpha = 0.001
    golden = (np.matmul(input_a.astype(np.float32), input_b.astype(np.float32)) + input_bias).astype(np.float32)
    golden = np.where(golden >= 0, golden, golden * alpha)
    is_equal = np.array_equal(output, golden)
    result = "success" if is_equal else "failed"
    print("compare {}.".format(result))
    # endregion 4
```

## region 1.构造kernel入参

可以构造numpy或者torch的tensor或tensor list作为调用kernel的输入。对于torch.Tensor，位置在npu或cpu上无要求。

假如有切片等修改shape的行为，则需要保证这些tensor在内存上是**连续的**，否则调用kernel时可能无法获取正确的结果。

判断tensor连续的方法：

```python
# torch.Tensor
if not t.is_contiguous():
    t = t.contiguous()
# numpy.ndarray
if not t.flags.contiguous:
    t = np.ascontiguousarray(t)
```

## region 2.调用算子tiling函数

这部分只用关注`mskpp.tiling_func`的参数，其他的保持原样即可。下面介绍这个mskpp接口。

### mskpp.tiling_func的定义

```python
def tiling_func(op_type: str, inputs: list = None, outputs: list = None, lib_path: str = None,
                inputs_info: list = None, outputs_info: list = None, attr=None,
                soc_version: str = None) -> TilingOutput
```

其中，只有`op_type`是必传的，其他参数都是可选参数。通常用户只需要关注4个参数：`op_type, inputs, outputs, lib_path`。

样例代码已展示接口返回值`TilingOutput`的所有字段，根据实际需求使用。另外，tiling结构体需要用户在tiling函数中自行打印。

**参数说明如下：**

#### op_type

**类型：**str

**介绍：**查找tiling函数的键值，受限于ascendc接口，查找顺序是：

1. 部署在cann包的算子
2. cann包已有的算子
3. lib_path指定的so

值取自算子tiling.cpp，注册的tiling类型，下面给出两种可能的注册形式：

```c++
// 形式1，填写MatmulLeakyreluCustom
OP_ADD(MatmulLeakyreluCustom);
// 形式2，填写GroupedMatmul
IMPL_OP_OPTILING(GroupedMatmul)
.Tiling(TilingGMM)
.TilingParse<GMMCompileInfo>(TilingPrepareForGMM);
```

#### inputs/outputs

**类型：**list[torch.Tensor or numpy.ndarray]

**介绍：**传入tensor或者tensor list，不使用的输入请传None，一般和inputs_info/outputs_info选一个使用

**约束：**

1. 通常和`inputs_info/outputs_info`只选一个填；
2. 支持numpy和torch的tensor混合传；
3. 不使用的某个tensor传`None`；
4. 支持tensor list，但是tensor list内部不能有None，典型非法输入：`[x1, None, x2]`、`[]`、`[None]`；
5. 默认所有tensor的format是nd，不是nd的情况需要在inputs_info/outputs_info手动指定；

以下给出两种确定算子输入输出的方法：

1. 看tiling定义源码：

![image](../pic/137a25c8b29340b2ec9fa949ee27c61d_551x426.png)

2. 看编译kernel得到的json：

![image](../pic/2e6ba66cd42942bb770769cee26ee290_351x724.png)

填写样例如下：

```python
M = 1024
N = 640
K = 256

input_a = np.random.randint(1, 10, [M, K]).astype(np.float16)
input_b = np.random.randint(1, 10, [K, N]).astype(np.float16)
input_bias = np.random.randint(1, 10, [N]).astype(np.float32)
inputs=[input_a, input_b, input_bias]

output = np.zeros([M, N]).astype(np.float32)
outputs=[output]

mskpp.tiling_func(
	inputs=inputs,
    outputs=outputs,
)
```

包含tensor list的样例：

```python
M = 1024
N = 640
K = 256

x1 = np.random.randint(1, 10, [M, K]).astype(np.float16)
x2 = np.random.randint(1, 10, [M, K]).astype(np.float16)
x3 = np.random.randint(1, 10, [M, K]).astype(np.float16)
x = [x1, x2, x3]
y = np.random.randint(1, 10, [M, K]).astype(np.float16)
# 第一个参数是包含3个tensor的tensor list
inputs=[x, y]

output = np.zeros([M, N]).astype(np.float32)
outputs=[output]

mskpp.tiling_func(
	inputs=inputs,
    outputs=outputs,
)
```

复杂输入样例：

```python
M = 1024
N = 640
K = 256
E = 16

x = torch.randint(1, 10, [M, K], dtype=torch.int8).npu()
weight = torch.randint(1, 10, [E, K, N], dtype=torch.int8).npu() #  FRACTAL_NZ
weight = torch_npu.npu_format_cast(weight.npu(), 29)
bias = None
scale = torch.randint(1, 10, [E, N], dtype=torch.float32).npu()
offset = None
antiquant_scale = None
antiquant_offset = None
group_list = gen_group_list(E, M)
per_token_scale = torch.normal(mean=0., std=0.1, size=(M,), dtype=torch.float32).npu()

inputs=[[x], [weight], bias, [scale], offset, antiquant_scale, antiquant_offset, group_list, [per_token_scale]]

inputs_info=[
    # 对应 [x]
    [],
    # 对应 [weight]，配置tensor list[0]的格式
    [{'format': 'FRACTAL_NZ'}]
]
```

#### inputs_info/outputs_info

**类型：**list[dict or list[dict]]

**介绍：**用字典形式描述输入输出tensor的信息，如果和inputs/outputs同时传，会以该参数为准。

**约束：**

1. 通常和`inputs/outputs`只选一个填；
2. 字典元素有白名单校验，只能有以下几项：
   - ori_shape：输入tensor的原始维度信息，含义参考gert::StorageShape类。
   - shape：输入tensor存储的维度信息，含义参考gert::StorageShape类。
   - dtype：输入tensor的数据类型，大小写不敏感。
   - ori_format：输入tensor的原始数据排布格式，默认为ND，大小写不敏感，含义参考gert::StorageFormat类。
   - format：输入tensor存储的数据排布格式，默认为ND，大小写不敏感，含义参考gert::StorageFormat类。
   - data_path：值依赖场景下，输入tensor的bin文件路径。本参数对于outputs_info**不生效**。
3. 对于每一个元素inputs_info[i]（outputs_info[i]同理），假如没有对应的inputs[i]，那么该元素必须至少包含`shape, dtype`

确定算子输入输出的方法见inputs/outputs的描述，下面给出一些案例：

输入案例1：

```python
M = 1024
N = 640
K = 256

inputs_info=[
    {"shape": [M, K], "dtype": "float16"},
    {"shape": [K, N], "dtype": "float16"},
    {"shape": [N], "dtype": "float32"},
]

outputs_info=[
    {"shape": [M, N], "dtype": "float32"},
]
mskpp.tiling_func(
	inputs_info=inputs_info,
    outputs_info=outputs_info,
)
```

tensor list场景输入案例：

```python
M = 1024
N = 640
K = 256

inputs_info=[
    # 第一个参数，tensor list里各个tensor的shape信息
    [
        {"shape": [M, K], "dtype": "float16"},
	    {"shape": [K, N], "dtype": "float16"},
    	{"shape": [N], "dtype": "float32"},
    ]
    # 第二个参数的shape
    {"shape": [M, K], "dtype": "float16"},
]

output = np.zeros([M, N]).astype(np.float32)
outputs_info=[
    {"shape": [M, N], "dtype": "float32"},
]
mskpp.tiling_func(
	inputs_info=inputs_info,
    outputs_info=outputs_info,
)
```

#### attr

**类型：**dict或者list[dict]

**介绍：**tiling函数依赖的attr。

**约束：**

1. 传入list时，其每个元素必须包含`name, dtype, value`，dtype有白名单校验；
2. attr名称或值如果是字符串，那必须由数字、大小写字母、下划线组成；
3. 传入dict时，不支持某个attr值为空list；

算子tiling涉及的attr可以通过源码查看

填写案例1：

```python
attr = [
    {
        "name": "scale_value",
        "dtype": "float",
        "value": 0.08838834764831843
    },
    {
        "name": "pre_tockens",
        "dtype": "int",
        "value": 65536
    },
    {
        "name": "input_layout",
        "dtype": "str",
        "value": "BNSD"
    },
    {
        "name": "a7",
        "dtype": "list_str",
        "value": ["asdf", "zxcv"]
    },
    {
        "name": "a8",
        "dtype": "list_list_int",
        "value": [[1, 2, 3, 4], [5, 6, 7, 8], [5646, 2345]]
    },
]
```

填写案例2：

```python
# 该方式禁止传入空list
attr={
    "a1": 1,
    "a2": False,
    "a3": "ssss",
    "a4": 1.2,
    "a5": [111.111, 111.222, 111.333],
    "a6": [True, False],
    "a7": ["asdf", "zxcv"],
    "a8": [[1, 2, 3, 4], [5, 6, 7, 8], [5646, 2345]],
    "a9": [111, 222, 333]
}
```

#### soc_version

**类型：**str

**介绍：**npu型号，不填时会获取当前平台信息

填写案例：

```python
soc_version="Ascend910B4"
```

#### lib_path

**类型：**str

**介绍：**算子tiling.so的路径，对于已部署在cann包的算子，不需要传递

填写案例：

```python
lib_path="./liboptiling.so"
```

## region 3.调用算子kernel

本部分需注意以下两点：

1. 函数`run_kernel`的入参需要和用户kernel函数实际入参保持一致，这些参数会被转发给用户kernel函数。例外：blockdim、tiling_key，这两个名称的参数不会被转发；
2. kernel_binary_file替换为实际kernel.o路径；

### mskpp.get_kernel_from_binary定义

```python
def get_kernel_from_binary(kernel_binary_file: str, kernel_type: str = None, tiling_key: int = None) -> CompiledKernel:
```

返回值按样例代码的调用方式执行即可，调用时可以配置`timeout=int, device_id=int`。

**参数说明如下：**

#### kernel_binary_file

**类型：**str

**介绍：**算子kernel.o的路径。如果需要用printf或者DumpTensor，该路径下需要有同名.json文件，若json的`"debugOptions"`有`"printf"`，则会使能上述两个接口。

#### kernel_type

**类型：**str，`mix, vec, cube`其中之一

**介绍：**指定算子类型，不指定时mskpp会尝试从kernel.o中获取，有相关日志打印，获取的类型错误时会导致算子运行失败。

#### tiling_key

**类型：**int

**介绍：**指定算子tiling_key，不指定时会使用上次调用mskpp.tiling_func的返回值。

## region 4.精度比较

mskpp目前没有提供精度比较函数，部分实例帖子有精度比较函数的样例，用户可以自定义比较方法来比较精度。

# 5.运行程序

命令行执行

```python
python3 xxx.py
```

# 6.工具临时文件说明

工具在执行过程中会在当前目录下会生成4个以`_mskpp_gen_`开头的文件，如下：

```
_mskpp_gen_binary_launch.cpp
_mskpp_gen_binary_module.so
_mskpp_gen_tiling.cpp
_mskpp_gen_tiling.so
```

# 7.npu支持情况说明

支持A2、A3、310p

# 8.问题定位

建议在tiling函数入口和出口增加自定义打印，检查执行情况

基本方向是：

1. 有python报错的，根据python提示处理，比如权限问题和函数入参错误
2. 没有python报错的，开plog日志，通常是因为算子执行失败

# 9.其他样例代码

一些基于sample代码仓的算子写的代码样例，文件路径依据实际替换

### sub

```python
import numpy as np
import mskpp


# This function's input arguments must exactly match the kernel function.
def sub_custom(input_x, input_y, output, workspace, tiling_data):
    kernel_binary_file = "./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/sub_custom/SubCustom_ee28f01d0bf2a796e851bf26764f1d82.o"
    kernel = mskpp.get_kernel_from_binary(kernel_binary_file)
    return kernel(input_x, input_y, output, workspace, tiling_data)


if __name__ == "__main__":
    # input/output tensor
    input_x = np.random.randint(100, size=(1, 999,)).astype(np.float16)
    input_y = np.random.randint(100, size=(1, 999,)).astype(np.float16)
    golden = (input_x - input_y).astype(np.float16)
    output = np.zeros([1, 999]).astype(np.float16)

    # shape info
    inputs_info = [{"shape": [1, 999], "dtype": "float16", "format": "ND"},
                   {"shape": [1, 999], "dtype": "float16", "format": "ND"},]
    outputs_info = [{"shape": [1, 999], "dtype": "float16", "format": "ND"}]
    attr = {}


    # tiling data
    tiling_output = mskpp.tiling_func(
        op_type="SubCustom",
        inputs_info=inputs_info, outputs_info=outputs_info,
        inputs=[input_x, input_y], outputs=[output],
        attr=attr,
        lib_path="./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/op_tiling/liboptiling.so",  # tiling代码编译产物
        # soc_version="", # 可选
    )
    blockdim = tiling_output.blockdim
    workspace_size = tiling_output.workspace_size
    tiling_data = tiling_output.tiling_data # numpy 数组
    workspace = np.zeros(workspace_size).astype(np.uint8) # workspace需要用户自行申请

    sub_custom(input_x, input_y, output, workspace, tiling_data)

    is_equal = np.array_equal(output, golden)
    result = "success" if is_equal else "failed"
    print("compare {}.".format(result))

```

### add

```python
import numpy as np
import mskpp


# This function's input arguments must exactly match the kernel function.
def add_custom(a, b, c, workspace, tiling_data):
    kernel_binary_file = "./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/add_custom/AddCustom_ab1b6750d7f510985325b603cb06dc8b.o"
    kernel = mskpp.get_kernel_from_binary(kernel_binary_file)
    return kernel(a, b, c, workspace, tiling_data)


if __name__ == "__main__":
    # input/output tensor
    a = np.random.randint(1, 5, [8, 4096]).astype(np.float16)
    b = np.random.randint(1, 5, [8, 4096]).astype(np.float16)
    c = np.zeros([8, 4096]).astype(np.float16)
    golden = (a + b).astype(np.float16)

    # shape info
    inputs_info = [{"format": "ND"}, # tensor信息补充
                   {"format": "ND"}]
    outputs_info = [{"format": "ND"}]
    attr = {}


    # tiling data
    tiling_output = mskpp.tiling_func(
        op_type="AddCustom",
        inputs=[a, b], outputs=[c],
        lib_path="./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/op_tiling/liboptiling.so",
    )
    blockdim = tiling_output.blockdim
    workspace_size = tiling_output.workspace_size
    tiling_data = tiling_output.tiling_data
    workspace = tiling_output.workspace

    add_custom(a, b, c, workspace, tiling_data)

    is_equal = np.array_equal(c, golden)
    result = "success" if is_equal else "failed"
    print("compare {}.".format(result))

```

### matmul

```python
import numpy as np
import mskpp


# This function's input arguments must exactly match the kernel function.
def matmul_custom(input_a, input_b, input_bias, output, workspace, tiling_data):
    kernel_binary_file = "./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/kernel/ascend910b/matmul_custom/MatmulCustom_60639c572d67590cdf443ee450a06634.o"
    kernel = mskpp.get_kernel_from_binary(kernel_binary_file)
    return kernel(input_a, input_b, input_bias, output, workspace, tiling_data)


if __name__ == "__main__":
    # input/output tensor
    M = 1024
    N = 640
    K = 256

    input_a = np.random.randint(1, 10, [M, K]).astype(np.float16)
    input_b = np.random.randint(1, 10, [K, N]).astype(np.float16)
    input_bias = np.random.randint(1, 10, [N]).astype(np.float32)
    output = np.zeros([M, N]).astype(np.float32)
    golden = (np.matmul(input_a.astype(np.float32), input_b.astype(np.float32)) + input_bias).astype(np.float32)

    # shape info
    inputs_info = [{"shape": [M, K], "dtype": "float16", "format": "ND"},
                   {"shape": [K, N], "dtype": "float16", "format": "ND"},
                   {"shape": [N], "dtype": "float", "format": "ND"}]
    outputs_info = [{"shape": [M, N], "dtype": "float", "format": "ND"}]
    attr = {}


    # tiling data
    tiling_output = mskpp.tiling_func(
        op_type="MatmulCustom",
        inputs_info=inputs_info, outputs_info=outputs_info,
        inputs=[input_a, input_b, input_bias], outputs=[output],
        attr=attr,
        lib_path="./build_out/_CPack_Packages/Linux/External/custom_opp_ubuntu_aarch64.run/packages/vendors/customize/op_impl/ai_core/tbe/op_tiling/liboptiling.so",  # tiling代码编译产物
        # soc_version="", # 可选
    )
    blockdim = tiling_output.blockdim
    workspace_size = tiling_output.workspace_size
    tiling_data = tiling_output.tiling_data # numpy 数组
    workspace = tiling_output.workspace

    matmul_custom(input_a, input_b, input_bias, output, workspace, tiling_data)

    is_equal = np.array_equal(output, golden)
    result = "success" if is_equal else "failed"
    print("compare {}.".format(result))
```

