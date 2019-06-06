import tensorflow as tf


def fnLayer(_input, _output_size, _activation='relu'):
    inp = _input.shape.as_list()[-1]
    ret = []
    ret.append(tf.Variable(tf.truncated_normal([inp, _output_size])))
    ret.append(tf.Variable(tf.truncated_normal([_output_size], stddev= 0.1)))
    if _activation == 'relu':
        ret.append(tf.nn.relu(tf.matmul(_input, ret[0]) + ret[1]))
    elif _activation == 'sigmoid':
        ret.append(tf.nn.sigmoid(tf.matmul(_input, ret[0]) + ret[1]))




class d_data:
    def __init__(self, _data):
        self.i = 0
        self.envs = self.data.keys()
        self.data = _data
    def init(self, _ratio):
        self.ratio = _ratio
        self.test_n = int(len(self.data) * self.ratio)
        self.train_n = len(self.data) - self.test_n
        for e in self.envs:
            self.l = train.shape[0]
            self.train = train
            self.test = test
    def getNext(self, _cnt):
        if (self.l < self.i):
            self.i = 0
        self.i += _cnt
        return self.train[self.i - _cnt:self.i]
    def getTestT(self):
        return self.test['true']
    def getTestX(self):
        return self.test['x']


class d_mlp:
    def __init__(self, _input_size, _hidden):
        self.input = tf.placeholder(tf.float32, [None, _input_size])
        #self.output_num = 1
        self.trues = tf.placeholder(tf.float32, [None, 1])
        self.h = []
        self.hl = _hidden
        self.hl.append(1)
        self.h.append(fnLayer(self.input, hl[0]))
        for idx, h in enumerate(_hidden[1:]):
            self.h.append(fnLayer(self.h[idx-1], h))
        #self.loss = -tf.reduce_sum(self.trues * tf.log(self.h[-1]))
        self.loss = tf.reduce_mean(tf.squared_difference(self.trues, self.h[-1]))
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss)
        self.acc = tf.reduce_mean(tf.abs(tf.divide(tf.subtract(self.h[-1],self.trues),(self.trues + 1e-10))))

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
                o, l, a = sess.run([net.h[-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: _data.getTestT(),
                    net.input: _data.getTestX()
                })
                print("Step %d||output: %d, loss: %d, accuracy: %d" % (i, o, l, a))
        

