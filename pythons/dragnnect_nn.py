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

def cnLayer(_input, _filter_num, _filter_size, _strides=[1,1,1,1], _cutoff='relu', _pool_kernel=[1,2,2,1], _pool_strides=[1,2,2,1], _isPool=True):
    _filter_size.append(_input.shape.as_list()[-1])
    _filter_size.append(_filter_num)
    
    ret = []
    ret.append(tf.Variable(tf.truncated_normal(_filter_size, stddev=0.1)))
    ret.append(tf.nn.conv2d(_input, ret[-1], strides=_strides, padding='SAME'))
    ret.append(tf.Variable(tf.truncated_normal([_filter_size[-1]], stddev=0.1)))
    # cutoff
    if _cutoff == 'relu':
        ret.append(tf.nn.relu(ret[1] + ret[2]))
    # pooling
    if _isPool:
        ret.append(tf.nn.max_pool(ret[3], ksize = _pool_kernel, strides = _pool_strides, padding = 'SAME'))
    return ret

def initCNLayer(_input, _filter_num, _filter_size, _strides = [1,1,1,1], 
_cutoff = 'relu', _pool_kernel = [1,2,2,1], _pool_strides = [1,2,2,1], _isPool = True):
    # W, H, B, cutted, P
    _filter_size.append(_input.shape.as_list()[-1])
    _filter_size.append(_filter_num)
    print(_filter_size)
    ret = []
    # Weights of a conv layer
    ret.append(tf.Variable(tf.truncated_normal(_filter_size, stddev = 0.1)))
    # Hidden(output) of a conv layer
    ret.append(tf.nn.conv2d(_input, ret[-1], strides = _strides, padding = 'SAME')) 
    # Bias of a conv layer. Its random var!
    # ret.append(tf.Variable(tf.constant(0.1, shape=[_filter_size[-1]])))
    ret.append(tf.Variable(tf.truncated_normal([_filter_size[-1]], stddev = 0.1)))
    # Cutoff
    if _cutoff == 'relu':
        ret.append(tf.nn.relu(ret[1] + ret[2]))
    # Pooling
    if _isPool:
        ret.append(tf.nn.max_pool(ret[3], ksize = _pool_kernel, strides = _pool_strides, padding = 'SAME'))
    return ret

class d_data:
    def __init__(self, _data):
        self.i = 0
        #self.envs = self.data.keys()
        self.r = _data['x'].shape[0]
        self.c = _data['x'].shape[1] + _data['trues'].shape[1]
        self.keys = _data['filename']
        self.meta = dict()
        for i, n in enumerate(self.keys):
            self.meta[n] = np.append(_data['x'][i], _data['trues'][i])
        #self.js = _data['js']
    def init(self, _ratio):
        self.ratio = _ratio
        self.test_n = int(self.r * self.ratio)
        self.train_n = self.r - self.test_n
        self.keys = np.random.permutation(self.keys)
        self.train = np.zeros((self.train_n, self.c))
        self.test = np.zeros((self.test_n, self.c))
        self.data = np.zeros((self.r, self.c))
        for i in range(self.train_n):
            self.train[i] = self.meta[self.keys[i]]
            self.data[i] = self.train[i]
        for i in range(self.test_n):
            self.test[i] = self.meta[self.keys[i + self.train_n]]
            self.data[i + self.train_n] = self.test[i]
    def getNext(self, _cnt):
        if (self.train_n < self.i):
            self.i = 0
        self.i += _cnt
        return self.train[self.i - _cnt:self.i][0:,0:self.c - 1], self.train[self.i - _cnt:self.i][0:,-1:], self.keys[self.i - _cnt:self.i]
    def getTestT(self):
        return self.test[0:,-1:], self.keys[self.train_n:]
    def getTestX(self):
        return self.test[0:,0:self.c - 1], self.keys[self.train_n:]
    def getAll(self):
        return self.data[0:,0:self.c - 1], self.data[0:,-1:], self.keys


class d_mlp:
    def __init__(self, _input_size, _hidden, _act = []):
        self.input_size = _input_size
        self.input = tf.placeholder(tf.float32, [None, _input_size])
        #self.output_num = 1
        self.trues = tf.placeholder(tf.float32, (None, 1))
        self.h = []
        self.hl = _hidden
        self.hl.append(1)
        self.h.append(fnLayer(self.input, self.hl[0]))
        if _act == []:
            for i in range(len(_hidden)):
                _act.append(None)
        for idx, h in enumerate(self.hl[1:-1]):
            self.h.append(fnLayer(self.h[idx-1][-1], h, _act[idx]))
        self.h.append(fnLayer(self.h[-2][-1], self.hl[-1], 'leaky_relu'))
        self.loss = tf.losses.mean_squared_error(self.trues, self.h[-1][-1])
        self.acc = tf.sqrt(tf.reduce_mean(tf.pow(tf.subtract(self.h[-1][-1],self.trues), 2)))
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss)
    def __str__(self):
        ret = ''
        ret += str(self.input_size) + "-" + str(self.hl)
        return ret

class d_cnn:
    def __init__(self, _input_size, _hidden, _act = [], _filter_size=[2,3]):
        self.input = tf.placeholder(tf.float32, [None, _input_size[0], _input_size[1]])
        #self.output_num = 1
        self.trues = tf.placeholder(tf.float32, (None, 1))
        self.h = []
        self.hl = _hidden
        self.hl.append(1)
        self.h.append(cnLayer(self.input, self.hl[0], _filter_size))
        # Output length of conv layer: _input_size[1] / 2 (= column / 2)
        if _act == []:
            for i in range(len(_hidden)):
                _act.append(None)
        for idx, h in enumerate(self.hl[1:-1]):
            self.h.append(fnLayer(self.h[idx-1][-1], h, _act[idx], _filter_size))
        self.h.append(fnLayer(self.h[-2][-1], self.hl[-1], 'leaky_relu'))
        #self.loss = -tf.reduce_sum(self.trues * tf.log(self.h[-1]))
        #self.loss = tf.reduce_mean(tf.squared_difference(self.trues, self.h[-1]))
        self.loss = tf.losses.mean_squared_error(self.trues, self.h[-1][-1])
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss)
        self.acc = tf.sqrt(tf.reduce_mean(tf.pow(tf.subtract(self.h[-1][-1],self.trues), 2)))

def train(net, _data, _ep = 10000, _print=False, _aim=0.1):
    i = 0
    init = tf.global_variables_initializer()
    conf = tf.ConfigProto(log_device_placement=False)
    with tf.Session(config=conf) as sess:
        sess.run(init)
        loss_val, acc_val = 0, 0
        et = 0
        out = dict()
        for _ in range(_ep):
            i += 1
            bx, bt, _ = _data.getNext(100)
            sess.run([net.train_step], feed_dict = {net.trues:bt, net.input:bx})
            if i % 500 == 0 or i == _ep:
                tr, _ = _data.getTestT()
                tx, _ = _data.getTestX()
                ax, ay, ak = _data.getAll()
                o, l, a = sess.run([net.h[-1][-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: tr,
                    net.input: tx
                })
                do, dl, da = sess.run([net.h[-1][-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: ay,
                    net.input: ax
                })
                print("Step " + str(i) + "||test) loss: %f, accuracy: %f ||all) loss: %f, acc: %f" % (l, a, dl, da))
                out['keys'] = ak
                out['outputs'] = do
                et = i
                if (a < _aim):
                    print("Training end.")
                    break

        # Save network
        # return experiment variable
        # [str(net), et, std(o), mean(o), out]
        ret = dict()
        ret['net'] = str(net)
        ret['iteration'] = et
        ret['std(o)'] = np.std(do)
        ret['mean(o)'] = np.mean(do)
        ret['out'] = out
        t = np.append(o, _data.getTestT()[0], 1)
        t = np.append(t, (o-_data.getTestT()[0]), 1)
        print(t)
        return ret
        #print()
        

