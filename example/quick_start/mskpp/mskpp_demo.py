import os
from mskpp import vadd, Tensor, Chip

def my_vadd(gm_x, gm_y, gm_z):
    # 向量Add的基本数据通路：
    # 被加数x: GM-UB
    # 加数y: GM-UB
    # 结果向量z: UB-GM

    # 定义和分配UB上的变量
    x = Tensor("UB")
    y = Tensor("UB")
    z = Tensor("UB")

    # 将GM上的数据移动到UB对应的内存空间上
    x.load(gm_x)
    y.load(gm_y)

    # 当前数据已加载到UB上，调用指令进行计算，结果保存在UB上
    out = vadd(x, y, z)()

    # 将UB上的数据移动到GM变量gm_z的地址空间上
    # vadd的返回值out是一个元组类型，通过下标取第0个元素
    gm_z.load(out[0])

if __name__ == '__main__':
    chip_name = os.getenv("MY_STUDY_VAR_CHIP_SOC_TYPE", "")
    with Chip("Ascend" + chip_name) as chip:  # 格式为Ascendxxxyy，其中xxxyy为用户实际使用的具体芯片SoC型号
        chip.enable_trace()  # 使能算子模拟流水图的功能，生成trace.json文件
        chip.enable_metrics() # 使能单指令及分PIPE的流水信息，生成Instruction_statistic.csv和Pipe_statistic.csv文件

        # 应用算子进行AI Core计算
        in_x = Tensor("GM", "FP16", [32, 48], format="ND")
        in_y = Tensor("GM", "FP16", [32, 48], format="ND")
        in_z = Tensor("GM", "FP16", [32, 48], format="ND")
        my_vadd(in_x, in_y, in_z)
