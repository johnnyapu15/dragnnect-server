# Dragnnect algorithms for experiments

# 1. basic data structure classes

# 2. json parser

# 3. algorithms


# import modules
import math
import numpy as np


# data structure classes
# class LineData:
#     def __init__(self, _id):
#         self.device_index = _id 
#         self.timeDelta = 0
#         self.timestamp = 0
#         self.lines = []
#     def load(self, _data):

# class device:

# 2. json parser

def jsonToData(_fileName):
    f = open(_fileName, 'r')
    j = json.loads(f.read())[0]
    f.close() 
    j['first']['lines'] = np.array(j['first']['lines'])
    j['second']['lines'] = np.array(j['second']['lines'])
    return j


# 3. Implemented algorithms
def getAngleDiff(_l0, _l1):
    t0 = math.atan2(_l0[1], _l0[0])
    t1 = math.atan2(_l1[1], _l1[0])
    return t0 - t1

def getRotated(_pnt, _theta):
    return np.array([
        [math.cos(_theta), -math.sin(_theta)],
        [math.sin(_theta), math.cos(_theta)]]).dot(_pnt)

def hueristic_uniform(_data):
    # _data:
    #   env
    #   subject
    #   first (line on first device)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin
    alpha = 0
    theta = 0
    vector_origin = np.nparray([0,0])

    s0 = _data['first']['lines'][0][0:2]
    e0 = _data['first']['lines'][-1][0:2]
    l0 = e0 - s0
    td0 = _data['first']['lines'][-1][2] - _data['first']['lines'][0][2]
    ts0 = _data['first']['timestamp']
    s1 = _data['second']['lines'][0][0:2]
    e1 = _data['second']['lines'][-1][0:2]
    l1 = e1 - s1
    td1 = _data['second']['lines'][-1][2] - _data['second']['lines'][0][2]
    ts1 = _data['second']['timestamp']
    
    # get alpha
    v = math.sqrt((l0*l0).sum()) / td0
    alpha = v * (td1 / (math.sqrt((l1*l1).sum())))

    # scale using alpha
    s1 = s1 * alpha
    e1 = e1 * alpha 
    l1 = e1 - s1 
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_s1 = getRotated(s1, theta)

    # get vector_origin
    d = v * (t)
    

    


    return [alpha, theta, vector_origin]


