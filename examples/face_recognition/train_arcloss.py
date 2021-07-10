# MIT License
#
# Copyright (c) 2018 Haoxintong
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
""""""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import time
import logging
import mxnet as mx
import numpy as np
from tqdm import tqdm
from mxnet import gluon, autograd as ag
from mxnet.gluon.data import DataLoader

from gluonfr.loss import *
from gluonfr.model_zoo import *
from gluonfr.data import get_recognition_dataset
from examples.face_recognition.utils import transform_test, transform_train, validate

num_gpu = 4
ctx = [mx.gpu(i) for i in range(num_gpu)]
batch_size = 128 * num_gpu
num_worker = 24
save_period = 500
iters = 200e3
lr_steps = [30e3, 60e3, 90e3, np.inf]

scale = 50
margin = 0.5
embedding_size = 128

lr = 0.1
momentum = 0.9
wd = 4e-5

train_set = get_recognition_dataset("emore", transform=transform_train)
train_data = DataLoader(train_set, batch_size, shuffle=True, num_workers=num_worker)

targets = ['lfw']
val_sets = [get_recognition_dataset(name, transform=transform_test) for name in targets]
val_datas = [DataLoader(dataset, batch_size, num_workers=num_worker) for dataset in val_sets]

net = get_mobile_facenet(train_set.num_classes, weight_norm=True, feature_norm=True)
net.initialize(init=mx.init.MSRAPrelu(), ctx=ctx)
# net.load_parameters(os.path.join(os.path.dirname(__file__),
#                                  "../../models/mobilefacenet-ring-it-185000.params"), ctx=ctx)
net.hybridize(static_alloc=True)

loss = ArcLoss(train_set.num_classes, m=margin, s=scale, easy_margin=False)

logger = logging.getLogger('TRAIN')
logger.setLevel("INFO")
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("./mobile-face-arcloss.log"))

train_params = net.collect_params()
# train_params.update(loss.params)
trainer = gluon.Trainer(train_params, 'nag', {'learning_rate': lr, 'momentum': momentum, 'wd': wd})
lr_counter = 0

logger.info([margin, scale, lr_steps, lr, momentum, wd, batch_size])

it, epoch = 0, 0

loss_mtc, acc_mtc = mx.metric.Loss(), mx.metric.Accuracy()
tic = time.time()

while it < iters + 1:

    for batch in tqdm(train_data):
        if it == lr_steps[lr_counter]:
            trainer.set_learning_rate(trainer.learning_rate * 0.1)
            lr_counter += 1

        datas = gluon.utils.split_and_load(batch[0], ctx_list=ctx, batch_axis=0, even_split=False)
        labels = gluon.utils.split_and_load(batch[1], ctx_list=ctx, batch_axis=0, even_split=False)

        with ag.record():
            ots = [net(X) for X in datas]
            outputs = [ot[1] for ot in ots]
            losses = [loss(yhat, y) for yhat, y in zip(outputs, labels)]

        for l in losses:
            ag.backward(l)

        trainer.step(batch_size)
        acc_mtc.update(labels, outputs)
        loss_mtc.update(0, losses)

        if (it % save_period) == 0 and it != 0:
            _, train_loss = loss_mtc.get()
            _, train_acc = acc_mtc.get()
            toc = time.time()

            logger.info('\n[epoch % 2d] [it % 3d] train loss: %.6f, train_acc: %.6f | time: %.6f' %
                        (epoch, it, train_loss, train_acc, toc - tic))

            results = validate(net, ctx, val_datas, targets)
            for result in results:
                logger.info('{}'.format(result))
            loss_mtc.reset()
            acc_mtc.reset()
            tic = time.time()
            net.save_parameters("../../models/mobilefacenet-arc-it-%d.params" % it)
        it += 1
    epoch += 1
