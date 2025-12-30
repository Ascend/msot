#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2025-2025. All rights reserved.

import numpy as np
import torch
import torch.nn.functional as F
import mskpp

blockdim = 40
batch_size = 128
num_classes = 1024
thres_hold = 0.0001

def get_kernel():
    src_path = "./cross_entropy.cpp"    # kernel实现文件
    kernel_name = "cross_entropy"       # 需调用的kernel名
    build_script = "../make.sh"         # kernel编译脚本
    config = mskpp.KernelInvokeConfig(src_path, kernel_name)
    gen_file = mskpp.Launcher(config).code_gen()
    kernel = mskpp.compile(build_script=build_script, launch_src_file=gen_file)
    return kernel


def cross_entropy(logit, label, output, workspace, syncspace, tiling):
    kernel = get_kernel()
    return kernel[blockdim](logit, label, output, workspace, syncspace, tiling, device_id=0)


def calc_cross_entropy_loss(logits, labels):
    logits = torch.from_numpy(logits)
    labels = torch.from_numpy(labels)
    probabilities = F.softmax(logits, dim=1)
    batch_size = logits.size(0)
    index = torch.arange(batch_size)
    true_probs = probabilities[index, labels]
    log_probs = -torch.log(true_probs)
    loss = torch.mean(log_probs)
    #loss = F.cross_entropy(logits, labels)
    return loss.numpy()


def data_compare(golden, npu_res):
    golden = golden.reshape(-1)
    npu_res = npu_res.reshape(-1)
    diff = np.abs(golden - npu_res)
    check_pass = True
    for i in range(len(diff)):
        if  diff[i] > thres_hold:
            check_pass = False
            print('idx:{} npu:{:.5f} golden:{:.5f}'.format(i, npu_res[i], golden[i]))
    if check_pass:
        print('precision check pass')
    else:
        print('precision check failed')


if __name__ == "__main__":
    logits = np.random.randn(batch_size, num_classes).astype(np.float32)
    labels = np.random.uniform(0, num_classes, [batch_size,]).astype(np.int64)
    golden = calc_cross_entropy_loss(logits, labels)
    npu_output = np.zeros([1,]).astype(np.float32)
    workspace = np.zeros([batch_size, num_classes]).astype(np.float32)
    syncspace = np.zeros([blockdim, 32]).astype(np.int8)
    tiling = np.zeros([3]).astype(np.int64)
    tiling[0] = batch_size
    tiling[1] = num_classes
    tiling[2] = blockdim
    cross_entropy(logits, labels, npu_output, workspace, syncspace, tiling)
    data_compare(golden, npu_output)

