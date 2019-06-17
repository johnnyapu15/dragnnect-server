import tensorflow as tf
import numpy as np
import time



def fnLayer(_input, _output_size, _activation='relu'):
    print(_input)
    inp = _input.shape.as_list()[-1]
    ret = []
    ret.append(tf.Variable(tf.truncated_normal([inp, _output_size], dtype=tf.float64)))
    ret.append(tf.Variable(tf.truncated_normal([_output_size], stddev= 0.1, dtype=tf.float64)))
    if _activation == 'relu':
        ret.append(tf.nn.relu(tf.matmul(_input, ret[0]) + ret[1]))
    elif _activation == 'leaky_relu':
        ret.append(tf.nn.leaky_relu(tf.matmul(_input, ret[0]) + ret[1]))
    elif _activation == 'sigmoid':
        ret.append(tf.nn.sigmoid(tf.matmul(_input, ret[0]) + ret[1]))
    elif _activation == 'tanh':
        ret.append(tf.nn.tanh(tf.matmul(_input, ret[0]) + ret[1]))
    tf.summary.histogram('fn', ret[-1])
    return ret

def cnLayer(_input, _filter_num, _filter_size, _strides=[1,1,1,1], _cutoff='relu', _pool_kernel=[1,2,2,1], _pool_strides=[1,2,2,1], _isPool=True):
    tmp = _filter_size[:]
    tmp.append(_input.shape.as_list()[-1])
    tmp.append(_filter_num)
    ret = []
    ret.append(tf.Variable(tf.truncated_normal(tmp, stddev=0.1, dtype=tf.float64)))
    ret.append(tf.nn.conv2d(_input, ret[-1], strides=_strides, padding='SAME'))
    ret.append(tf.Variable(tf.truncated_normal([tmp[-1]], stddev=0.1, dtype=tf.float64)))
    # cutoff
    if _cutoff == 'relu':
        ret.append(tf.nn.relu(ret[1] + ret[2]))
    # pooling
    if _isPool:
        ret.append(tf.nn.max_pool(ret[3], ksize = _pool_kernel, strides = _pool_strides, padding = 'SAME'))
    tf.summary.histogram('cn', ret[-1])
    return ret

def initCNLayer(_input, _filter_num, _filter_size, _strides = [1,1,1,1], 
_cutoff = 'relu', _pool_kernel = [1,2,2,1], _pool_strides = [1,2,2,1], _isPool = True):
    # W, H, B, cutted, P
    _filter_size.append(_input.shape.as_list()[-1])
    _filter_size.append(_filter_num)
    print(_filter_size)
    ret = []
    # Weights of a conv layer
    ret.append(tf.Variable(tf.truncated_normal(_filter_size, stddev = 0.1), dtype=tf.float64))
    # Hidden(output) of a conv layer
    ret.append(tf.nn.conv2d(_input, ret[-1], strides = _strides, padding = 'SAME')) 
    # Bias of a conv layer. Its random var!
    # ret.append(tf.Variable(tf.constant(0.1, shape=[_filter_size[-1]])))
    ret.append(tf.Variable(tf.truncated_normal([_filter_size[-1]], stddev = 0.1), dtype=tf.float64))
    # Cutoff
    if _cutoff == 'relu':
        ret.append(tf.nn.relu(ret[1] + ret[2]))
    # Pooling
    if _isPool:
        ret.append(tf.nn.max_pool(ret[3], ksize = _pool_kernel, strides = _pool_strides, padding = 'SAME'))
    return ret

def dataToTensor(_data, _ratio, _batch):
    meta = dict()
    r = len(_data['x'])
    c = len(_data['x'][0])
    train_n = int(r * _ratio)
    test_n = r - train_n 
    keys = _data['filename']
    meta = dict()
    for i, e in enumerate(keys):
        meta[e] = (_data['x'][i], _data['trues'][i])
    d_train = dict()
    d_train['x'] = np.zeros((train_n, c))
    d_train['t'] = np.zeros((train_n, 1))
    d_train['f'] = []

    d_test = dict()
    d_test['x'] = np.zeros((test_n, c))
    d_test['t'] = np.zeros((test_n, 1))
    d_test['f'] = []

    permed = np.random.permutation(keys)
    for i, e in enumerate(permed):
        if (i < train_n):
            d_train['x'][i] = meta[e][0]
            d_train['t'][i] = meta[e][1]
            d_train['f'].append(e)
        else:
            d_test['x'][i - train_n] = meta[e][0]
            d_test['t'][i - train_n] = meta[e][1]
            d_test['f'].append(e)
    alldata = tf.data.Dataset.from_tensor_slices((_data['x'], _data['trues'], _data['filename']))
    alldata = alldata.shuffle(10000000).repeat().batch(_batch)
    alldata_iterator = alldata.make_one_shot_iterator()
    alldata_nxt = alldata_iterator.get_next()

    traindata = tf.data.Dataset.from_tensor_slices((d_train['x'], d_train['t'], d_train['f']))
    traindata = traindata.shuffle(10000000).repeat().batch(_batch)
    traindata_iterator = traindata.make_one_shot_iterator()
    traindata_nxt = traindata_iterator.get_next()

    testdata = tf.data.Dataset.from_tensor_slices((d_test['x'], d_test['t'], d_test['f']))
    testdata = testdata.shuffle(10000000).repeat().batch(_batch)
    testdata_iterator = testdata.make_one_shot_iterator()
    testdata_nxt = testdata_iterator.get_next()
    return traindata_nxt, testdata_nxt, alldata_nxt


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

class d_data2:
    def __init__(self, _data):
        self.i = 0
        #self.envs = self.data.keys()
        self.r = _data['x'].shape[0]
        self.in_shape = _data['x'].shape[1:3]
        self.keys = _data['filename']
        self.meta = (dict(), dict())
        for i, n in enumerate(self.keys):
            self.meta[0][n] = _data['x'][i]
            self.meta[1][n] = _data['trues'][i]
        #self.js = _data['js']
    def init(self, _ratio):
        self.ratio = _ratio
        self.test_n = int(self.r * self.ratio)
        self.train_n = self.r - self.test_n
        self.keys = np.random.permutation(self.keys)
        self.train = (np.zeros((self.train_n, self.in_shape[0], self.in_shape[1])), np.zeros((self.train_n, 1)))
        self.test = (np.zeros((self.test_n, self.in_shape[0], self.in_shape[1])), np.zeros((self.test_n, 1)))
        self.data = (np.zeros((self.r, self.in_shape[0], self.in_shape[1])), np.zeros((self.r, 1))) 
        for i in range(self.train_n):
            self.train[0][i] = self.meta[0][self.keys[i]]
            self.train[1][i] = self.meta[1][self.keys[i]]
            self.data[0][i] = self.meta[0][self.keys[i]]
            self.data[1][i] = self.meta[1][self.keys[i]]
        for i in range(self.test_n):
            self.test[0][i] = self.meta[0][self.keys[i + self.train_n]]
            self.test[1][i] = self.meta[1][self.keys[i + self.train_n]]
            self.data[0][i + self.train_n] = self.meta[0][self.keys[i]]
            self.data[1][i + self.train_n] = self.meta[1][self.keys[i]]
    def getNext(self, _cnt):
        if (self.train_n < self.i):
            self.i = 0
        self.i += _cnt
        return self.train[0][self.i - _cnt:self.i], self.train[1][self.i - _cnt:self.i], self.keys[self.i - _cnt:self.i]
    def getTest(self):
        return self.test[0], self.test[1], self.keys[self.train_n:]
    def getTrain(self):
        return self.train[0], self.train[1], self.keys[0:self.train_n]
    def getAll(self):
        return self.data[0], self.data[1], self.keys

class d_mlp2:
    def __init__(self, _train, _hidden, _act = []):
        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        # self.input_size = _input_size
        # self.input = tf.placeholder(tf.float32, [None, _input_size])
        self.input = _train[0]
        #self.output_num = 1
        #self.trues = tf.placeholder(tf.float32, (None, 1))
        self.trues = _train[1]
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
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss, global_step=self.global_step)
    def __str__(self):
        ret = ''
        ret += str(self.hl)
        return ret

class d_mlp:
    def __init__(self, _input_size, _hidden, _act = []):
        print("dnn init...")
        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        self.input_size = _input_size
        self.input = tf.placeholder(tf.float64, [None, _input_size, 1])
        self.input_reshaped = tf.reshape(self.input, (-1, _input_size))
        #self.output_num = 1
        self.trues = tf.placeholder(tf.float64, (None, 1))
        self.h = []
        self.hl = _hidden
        self.hl.append(1)
        self.h.append(fnLayer(self.input_reshaped, self.hl[0]))
        if _act == []:
            for i in range(len(_hidden)):
                _act.append(None)
        for idx, h in enumerate(self.hl[1:-1]):
            self.h.append(fnLayer(self.h[idx-1][-1], h, _act[idx]))
        self.h.append(fnLayer(self.h[-2][-1], self.hl[-1], 'leaky_relu'))
        self.loss = tf.losses.mean_squared_error(self.trues, self.h[-1][-1])
        self.loss_summ = tf.summary.scalar("loss", self.loss)
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss, global_step=self.global_step)
        self.acc = tf.sqrt(tf.reduce_mean(tf.pow(tf.subtract(self.h[-1][-1],self.trues), 2)))
        self.acc_summ = tf.summary.scalar("acc", self.acc)
        self.keep_prob = tf.placeholder(tf.float64)

    def __str__(self):
        ret = ''
        ret += str(self.input_size) + "-" + str(self.hl)
        return ret

class d_cnn:
    def __init__(self, _input_size, _hidden, _act = [], _filter_size=[2,3]):
        print("cnn init...")
        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        self.input = tf.placeholder(tf.float64, [None, _input_size[0], _input_size[1]])
        self.input_shaped = tf.reshape(self.input, (-1, _input_size[0], _input_size[1], 1))
        #self.output_num = 1
        self.trues = tf.placeholder(tf.float64, (None, 1))
        self.h = []
        self.hl = _hidden
        self.hl.append(1)
        self.cn = cnLayer(self.input_shaped, self.hl[0], _filter_size)
        tmp = 1
        for i, e in enumerate(np.array(self.cn[-1].shape[1:])):
            tmp *= e
        self.cn.append(tf.reshape(self.cn[-1],(-1, int(tmp))))
        self.hl[0] = int(_input_size[1] / 2 * self.hl[0])
        self.h.append(self.cn)
        # Output length of conv layer: _input_size[1] / 2 (= column / 2)
        if _act == []:
            for i in range(len(_hidden)):
                _act.append(None)
        for idx, h in enumerate(self.hl[1:-1]):
            self.h.append(fnLayer(self.h[idx-1][-1], h, _act[idx]))
        #self.h.append(fnLayer(self.h[-2][-1], self.hl[-1], 'leaky_relu'))
        # set output layer with dropout
        ret = []
        ret.append(tf.Variable(tf.truncated_normal([self.hl[-2], 1], dtype=tf.float64)))
        ret.append(tf.Variable(tf.truncated_normal([1], stddev= 0.1, dtype=tf.float64)))
        self.keep_prob = tf.placeholder(tf.float64)
        self.drop = tf.nn.dropout(self.h[-1][-1], self.keep_prob)
        ret.append(tf.nn.leaky_relu(tf.matmul(self.drop, ret[0]) + ret[1]))
        self.h.append(ret)
        tf.summary.histogram('output', ret[-1])
        #self.loss = -tf.reduce_sum(self.trues * tf.log(self.h[-1]))
        #self.loss = tf.reduce_mean(tf.squared_difference(self.trues, self.h[-1]))
        self.loss = tf.losses.mean_squared_error(self.trues, self.h[-1][-1])
        self.loss_summ = tf.summary.scalar("loss", self.loss)
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.loss, global_step=self.global_step)
        self.acc = tf.sqrt(self.loss)
        self.acc_summ = tf.summary.scalar("acc", self.acc)


def train(net, _data, _ep = 10000, _print=False, _aim=0.1, _savename = 'dnn.ckpt'):
    init = tf.global_variables_initializer()
    conf = tf.ConfigProto(log_device_placement=False)
    conf.gpu_options.per_process_gpu_memory_fraction = 0.25
    with tf.Session(config=conf) as sess:
        saver = tf.train.Saver(tf.global_variables())
        # merged = tf.summary.merge_all()
        # writer = tf.summary.FileWriter("./logs/" + _savename)
        #writer.add_graph(sess.graph)
        sess.run(init)
        loss_val, acc_val = 0, 0
        it = 0
        out = dict()
        testdata = _data.getTest()
        traindata = _data.getTrain()
        alldata = _data.getAll()
        #time
        st = 0
        et = 0
        for _ in range(_ep):
            bx, bt, _ = _data.getNext(100)
            _, i = sess.run([net.train_step, net.global_step], \
                feed_dict = {
                    net.trues:bt, net.input:bx, net.keep_prob:0.8
                    })
            #writer.add_summary(summary, global_step=i)
            if i % 500 == 0 or i == _ep:
                et = time.time()
                o, l, a = sess.run([net.h[-1][-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: testdata[1],
                    net.input: testdata[0],
                    net.keep_prob:1
                })
                to, tl, ta = sess.run([net.h[-1][-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: traindata[1],
                    net.input: traindata[0],
                    net.keep_prob:1
                })
                do, dl, da = sess.run([net.h[-1][-1], net.loss, net.acc],
                feed_dict = {
                    net.trues: alldata[1],
                    net.input: alldata[0],
                    net.keep_prob:1
                })
                print("Step " + str(i) + "||test) loss: %f, acc: %f ||train) loss: %f, acc: %f ||all) loss: %f, acc: %f || time: %.2f s" % (l, a, tl, ta, dl, da, (et-st)))
                out['keys'] = alldata[2]
                out['outputs'] = do
                it = i
                st = time.time()
                if (a < _aim) | (dl < 1e-6):
                    print("Training success.")
                    break
        saver.save(sess, './model/' + _savename, global_step=net.global_step)

        # Save network
        
        # return experiment variable
        # [str(net), et, std(o), mean(o), out]
        
        ret = dict()
        ret['net'] = str(net)
        ret['iteration'] = it
        ret['std(o)'] = np.std(do)
        ret['mean(o)'] = np.mean(do)
        ret['out'] = out
        t = np.append(o, testdata[1], 1)
        t = np.append(t, (o-testdata[1]), 1)
        print(t)
        return ret, a, da
        #print()
        

def train2(net, _data, _ep = 10000, _print=False, _aim=0.1, _modelname = 'dnn.ckpt'):
    init = tf.global_variables_initializer()
    conf = tf.ConfigProto(log_device_placement=True)
    with tf.Session(config=conf) as sess:
        saver = tf.train.Saver(tf.global_variables())
        sess.run(init)
        loss_val, acc_val = 0, 0
        et = 0
        out = dict()
        for _ in range(_ep):
            bx, bt, _ = _data[0]
            _, i = sess.run([net.train_step, net.global_step], feed_dict = {net.trues:bt, net.input:bx})
            if i % 500 == 0 or i == _ep:
                tx, tr, _ = _data[1]
                ax, ay, ak = _data[2]
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
                    print("Training success.")
                    break
        saver.save(sess, './model/' + _modelname, global_step=net.global_step)

        # Save network
        
        # return experiment variable
        # [str(net), et, std(o), mean(o), out]
        
        ret = dict()
        ret['net'] = str(net)
        ret['iteration'] = et
        ret['std(o)'] = np.std(do)
        ret['mean(o)'] = np.mean(do)
        ret['out'] = out
        t = np.append(o, tr, 1)
        t = np.append(t, (o-tr), 1)
        print(t)
        return ret
        #print()