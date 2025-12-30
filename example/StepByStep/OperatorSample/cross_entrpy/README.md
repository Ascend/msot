# OperatorSample

cross_entrpy为交叉熵损失函数，为大语言模型中常见的损失函数；
api包含两个输入logits和labels;
logits shape为：[batch_size, num_class];
labels shape为：[batch_size]，并且每个元素取值范围为[0, num_class);
计算公式如下：
Ypred = softmax(logits)
Ytrue = onehot(labels)
loss = -1/batch_size * Sum[Ytrue * log(Ypred)]

# 运行方式
python3 sample_cross_entrpy.py

# 说明信息
1. 目前只支持float32数据类型；
2. 支持的num_class范围为[1, 24000];
