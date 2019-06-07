import tensorflow as tf
import numpy as np



def fnLayer(_input, _output_size, _activation='relu'):
    inp = _input.shape.as_list()[-1]
    ret = []
    ret.append(tf.Variable(tf.truncated_normal([inp, _output_size])))
    ret.append(tf.Variable(tf.truncated_normal([_output_size], stddev= 0.1)))
    if _activation == 'relu':
        ret.append(tf.nn.relu(tf.matmul(_input, ret[0]) + ret[1]))
    elif _activation == 'leaky_relu':
        ret.append(tf.nn.leaky_relu(tf.matmul(_input, ret[0]) + ret[1]))
    elif _activation == 'sigmoid':
        ret.append(tf.nn.sigmoid(tf.matmul(_input, ret[0]) + ret[1]))
    return ret



class d_data:
    def __init__(self, _data):
        self.i = 0
        #self.envs = self.data.keys()
        self.r = _data['x'].shape[0]
        self.c = _data['x'].shape[1] + 1
        self.data = np.zeros((self.r, self.c))
        for i in range(self.r):
            self.data[i] = np.append(_data['x'][i], _data['trues'][i])
        print(self.data)
        
    def init(self, _ratio):
        self.ratio = _ratio
        self.test_n = int(self.r * self.ratio)
        self.train_n = self.r - self.test_n
        tmp = np.random.permutation(self.data.transpose()).transpose()
        self.train = tmp[0:self.train_n]
        self.test = tmp[self.train_n:]   
    def getNext(self, _cnt):
        if (self.train_n < self.i):
            self.i = 0
        self.i += _cnt
        return self.train[self.i - _cnt:self.i][0:,0:self.c - 1], self.train[self.i - _cnt:self.i][0:,-1:]
    def getTestT(self):
        return self.test[0:,-1:]
    def getTestX(self):
        return self.test[0:,0:self.c - 1]


class d_mlp:
    def __init__(self, _input_size, _hidden):
        self.input = tf.placeholder(tf.float32, [None, _input_size])
        #self.output_num = 1
        self.trues = tf.placeholder(tf.float32, (None, 1))
        self.h = []
        self.hl = _hidden
        self.hl.append(1)
        self.h.append(fnLayer(self.input, self.hl[0]))
        for idx, h in enumerate(self.hl[1:-1]):
            self.h.append(fnLayer(self.h[idx-1][-1], h))
        self.h.append(fnLayer(self.h[-2][-1], self.hl[-1], 'leaky_relu'))
        #self.loss = -tf.reduce_sum(self.trues * tf.log(self.h[-1]))
        #self.loss = tf.reduce_mean(tf.squared_difference(self.trues, self.h[-1]))
        self.loss = tf.losses.mean_squared_error(self.trues, self.h[-1][-1])
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss)
        self.acc = tf.reduce_mean(tf.abs(tf.divide(tf.subtract(self.h[-1][-1],self.trues),(self.trues + 1e-10))))

def train(net, _data, _ep = 10000, _print=False):
    i = 0
    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        loss_val, acc_val = 0, 0
        for _ in range(_ep):
            i += 1
            bx, bt = _data.getNext(40)
            sess.run([net.train_step], feed_dict = {net.trues:bt, net.input:bx})
            if i % 500 == 0 or i == _ep:
                o, l, a = sess.run([net.h[-1][-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: _data.getTestT(),
                    net.input: _data.getTestX()
                })
                dl, da = sess.run([net.loss, net.acc],
                feed_dict = {
                    net.trues: bt,
                    net.input: bx
                })
                print("Step " + str(i) + "|| loss: %f, accuracy: %f || trains) loss: %f, acc: %f" % (l, a, dl, da))
        t = np.append(o, _data.getTestT(), 1)
        t = np.append(t, (o-_data.getTestT()), 1)
        print(t)
        #print()
        

