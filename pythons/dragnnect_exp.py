# Dragnnect algorithms for experiments

# 1. basic data structure classes

# 2. json parser

# 3. algorithms


# import modules
import math
import numpy as np
import json

func_args = ["using_2_lines"]

# data structure classes

class Output: 
    def __init__(self, _alpha, _theta, _vo):
        self.alpha = _alpha
        self.theta = _theta
        if type(_vo) != np.array:
            v = np.array(_vo)
        else:
            v = _vo
        self.vo = v
    def __str__(self):
        ret = ""
        ret += "--Alpha: " + str(self.alpha)
        ret += "\n--Theta: " + str(self.theta)
        ret += "\n--V_o: " + str(self.vo)
        return ret
    def __repr__(self):
        return self.__str__()
    def __sub__(self, _o):
        return Output(
            self.alpha - _o.alpha,
            self.theta - _o.theta,
            self.vo - _o.vo
        )
    def getNparray(self):
        return np.array(
            (
                self.alpha, 
                self.theta,
                self.vo[0],
                self.vo[1]
            )
        )
    def getResidual(self, _true):
        # y - o
        return _true - self        
        
class LineData:
    def __init__(self, _id):
        self.device_index = _id
        self.timeDelta = 0
        self.timestamp = 0 #server timestamp
        self.lines = []
    def set(self, _lines, _timestamp):
        self.lines = _lines
        self.timeDelta = _lines[-1][2] - _lines[0][2]
        self.timestamp = _timestamp

class DeviceArrangement:
    def __init__(self, _id):
        self.device_name = ""
        self.device_id = _id
        self.linked_dev = 0
        self.up = np.zeros((3,))
        self.width = 0
        self.height = 0
        self.ntpDelay = 0
        self.ntpTimes = 0
        self.alpha = 1            # alpha of DPI
        self.rot = np.zeros((3,)) # theta
        self.pos = np.zeros((3,)) # origin
    def __str__(self):
        ret = ""
        ret += "Device_id: " + str(self.device_id)
        ret += "\nSize: " + str(self.width) + ", " + str(self.height)
        ret += "\nPosition: " + str(self.pos)
        ret += "\nRotation: " + str(self.rot)
        ret += "\nAlpha: " + str(self.alpha)
        return ret
    def __repr__(self):
        return self.__str__()
    def init(self):
        self.rot = np.zeros((3))
        self.pos = np.zeros((3))
        self.alpha = 1
        
    def setDeviceSize(self, _w, _h):
        if self.width == 0:
            self.width = _w 
            self.height = _h 
        elif (_w == 0) & (_h == 0):
            self.width = 0
            self.height = 0
    def get2dPoints(self):
        # Scaling
        w = self.width * self.alpha
        h = self.height * self.alpha
        # Get points
        p0 = np.array((self.pos[0], self.pos[2]))
        p1 = p0 + getRotated(np.array((w, 0)), self.rot[1])
        p2 = p0 + getRotated(np.array((0, h)), self.rot[1])
        p3 = p0 + getRotated(np.array((w, h)), self.rot[1])
        return [list(np.around(p0,3)), list(np.around(p1,3)), list(np.around(p3,3)), list(np.around(p2,3))]
    def get2dPointsArray(self):
        # Scaling
        w = self.width * self.alpha
        h = self.height * self.alpha
        # Get points
        p0 = np.array((self.pos[0], self.pos[2]))
        p1 = p0 + getRotated(np.array((w, 0)), self.rot[1])
        p2 = p0 + getRotated(np.array((0, h)), self.rot[1])
        p3 = p0 + getRotated(np.array((w, h)), self.rot[1])
        return np.array((p0, p1, p3, p2))
    def link(self, _dev, _data):
        # _data: [alpha, theta, Vo]
        # rotation for 2d: y-axis of 3d
        _dev.linked_dev = self.device_id
        _dev.alpha = _data.alpha * self.alpha
        _dev.rot[1] = _data.theta + self.rot[1]
        _dev.pos[0] = _data.vo[0] + self.pos[0]
        _dev.pos[2] = _data.vo[1] + self.pos[2]


# 2. json parser
def jsonToEnv(_fileName):
    f = open(_fileName, 'r')
    j = json.loads(f.read())
    f.close()
    ret = dict()
    for e in j.keys():
        t = j[e]
        ret[e] = Output(t['alpha'], t['theta'], t['vo'])
    return ret

def jsonToLineData(_fileName):
    f = open(_fileName, 'r')
    j = json.loads(f.read())
    f.close() 
    j['first']['lines'] = np.array(j['first']['lines'])
    j['second']['lines'] = np.array(j['second']['lines'])
    return j
def jsonToDeviceData(_fileName):
    f = open(_fileName, 'r')
    j = json.loads(f.read())
    f.close() 
    i0 = j['first']['dev_index']
    i1 = j['second']['dev_index']
    ret = dict()
    ret[str(i0)] = (j['first']['width'], j['first']['height'])
    ret[str(i1)] = (j['second']['width'], j['second']['height'])
    return ret

## For algorithm exp
def jsonToData(_fileName):
    f = open(_fileName, 'r')
    j = json.loads(f.read())
    f.close() 
    j['line_num'] = int(j['line_num'])
    j['first']['lines'] = np.array(j['first']['lines'])
    j['second']['lines'] = np.array(j['second']['lines'])
    i0 = j['first']['dev_index']
    i1 = j['second']['dev_index']
    d0 = DeviceArrangement(i0)
    d0.setDeviceSize(j['first']['width'], j['first']['height'])
    d1 = DeviceArrangement(i1) 
    d1.setDeviceSize(j['second']['width'], j['second']['height'])
    return j, [d0, d1]

# def exp(_fileName, _algorithm):
#     js, devs = jsonToData(_fileName)
#     output = 0
#     if _algorithm == 'heuristic_uniform':
#         output = heuristic_uniform(js)
#     devs[0].link(devs[1], output)
def getMSEScalar(_output, _true):
    ret = np.sum((_true - _output)**2) / 2
    return ret
def getMSEVector(_output, _true):
    # columns: alpha, theta, vo[0], vo[1]
    # rows: number of data
    if (type(_output) == Output):
        o = _output.getNparray()
    elif (type(_output) == list):
        o = np.array(_output)
    else:
        o = _output
    if (type(_true) == Output):
        t = _true.getNparray()
    elif (type(_true) == list):
        t = np.array(_true)
    else:
        t = _true
    if (len(o.shape) == 1):
        o = np.array([o])
        t = np.array([t])
    ret = []
    for i in range(4):
        ret.append((np.sum((t[0:,i] - o[0:,i]) ** 2))/2)
    return np.array(ret)
        
# 3. Implemented algorithms
def getAngleDiff(_l0, _l1):
    t0 = math.atan2(_l0[1], _l0[0])
    t1 = math.atan2(_l1[1], _l1[0])
    return t0 - t1

def getRotated(_pnt, _theta):
    return np.array([
        [math.cos(_theta), -math.sin(_theta)],
        [math.sin(_theta), math.cos(_theta)]]).dot(_pnt)


## Heuristic_basic algorithm
def heuristic_basic(_data, **arg):
    # _data:
    #   env
    #   subject
    #   first (line on first device, scaled by self.alpha)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin
    
    #set default args
    for a in func_args:
        if a not in arg.keys():
            arg[a] = False
            
    alpha = 1
    theta = 0
    vector_origin = np.ndarray([0,0])

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
    if arg['using_2_lines']:
        v = (
            math.sqrt((l0*l0).sum()) / td0 + \
            math.sqrt((l1*l1).sum()) / td1) / 2
    else:
        v = math.sqrt((l0*l0).sum()) / td0
    alpha = v * (td1 / (math.sqrt((l1*l1).sum())))

    # scale using alpha
    # In heuristic-basic alpha is always 1 
    alpha = 1
    s1 = s1 * alpha
    e1 = e1 * alpha 
    l1 = e1 - s1 
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_s1 = getRotated(s1, theta)

    # get vector_origin
    d = v * ((_data['second']['lines'][0][2] + ts1) - (_data['first']['lines'][-1][2] + ts0))
    vd = d * (l0 / math.sqrt((l0*l0).sum()))
    vector_origin = vd + e0 - rot_s1
    
    return Output(alpha, theta, vector_origin)


def SimpleAvg(_data, **arg):
    # _data:
    #   env
    #   subject
    #   first (line on first device, scaled by self.alpha)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin

    #set default args
    for a in func_args:
        if a not in arg.keys():
            arg[a] = False
            
    alpha = 1
    theta = 0
    vector_origin = np.ndarray([0,0])

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
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_l1 = []
    for l in _data['second']['lines']:
        rot_l1.append(np.append(getRotated(l[0:2], theta), l[2]))
    rot_l1 = np.array(rot_l1)

    # calculate velocities using simple average
    velos = []
    weights = []
    l0s = _data['first']['lines']
    for i in range(1,l0s.shape[0]):
        velos.append(
                np.sqrt(np.sum((l0s[i][0:2]-l0s[i-1][0:2])**2))/(l0s[i][2]-l0s[i-1][2])
            )
        weights.append((l0s[i][2]-l0s[i-1][2]))
    if arg['using_2_lines']:
        l1s = _data['second']['lines']
        for i in range(1,l1s.shape[0]):
            velos.append(
                    np.sqrt(np.sum((l1s[i][0:2]-l1s[i-1][0:2])**2))/(l1s[i][2]-l1s[i-1][2])
                )
            weights.append((l1s[i][2]-l1s[i-1][2]))
    velos = np.array(velos)
    v = np.average(velos, weights=weights)
    
    d = v * ((_data['second']['lines'][0][2] + ts1) - (_data['first']['lines'][-1][2] + ts0))
    vd = d * (l0 / math.sqrt((l0*l0).sum()))
    vector_origin = vd + e0 - rot_l1[0][0:2]
    
    return Output(alpha, theta, vector_origin)


def WeightedAvg(_data, **arg):
    # _data:
    #   env
    #   subject
    #   first (line on first device, scaled by self.alpha)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin

    #set default args
    for a in func_args:
        if a not in arg.keys():
            arg[a] = False
            
    alpha = 1
    theta = 0
    vector_origin = np.ndarray([0,0])

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
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_l1 = []
    for l in _data['second']['lines']:
        rot_l1.append(np.append(getRotated(l[0:2], theta), l[2]))
    rot_l1 = np.array(rot_l1)

    # calculate velocities using weighted average
    velos = []
    weights = []
    l0s = _data['first']['lines']
    for i in range(1,l0s.shape[0]):
        velos.append(
                np.sqrt(np.sum((l0s[i][0:2]-l0s[i-1][0:2])**2))/(l0s[i][2]-l0s[i-1][2])
            )
        weights.append((l0s[i][2]-l0s[i-1][2]) * i)
    if (arg['using_2_lines']):
        l1s = _data['second']['lines']
        for i in range(1,l1s.shape[0]):
            velos.append(
                    np.sqrt(np.sum((l1s[i][0:2]-l1s[i-1][0:2])**2))/(l1s[i][2]-l1s[i-1][2])
                )
            weights.append((l1s[i][2]-l1s[i-1][2]) * i)
    velos = np.array(velos)
    v = np.average(velos, weights=np.array((
        weights
    )))
    
    d = v * ((_data['second']['lines'][0][2] + ts1) - (_data['first']['lines'][-1][2] + ts0))
    vd = d * (l0 / math.sqrt((l0*l0).sum()))
    vector_origin = vd + e0 - rot_l1[0][0:2]
    
    return Output(alpha, theta, vector_origin)

def ExponentialWeightedAvg2(_data, **arg):
    # _data:
    #   env
    #   subject
    #   first (line on first device, scaled by self.alpha)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin

    #set default args
    for a in func_args:
        if a not in arg.keys():
            arg[a] = False

    alpha = 1
    theta = 0
    vector_origin = np.ndarray([0,0])

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
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_l1 = []
    for l in _data['second']['lines']:
        rot_l1.append(np.append(getRotated(l[0:2], theta), l[2]))
    rot_l1 = np.array(rot_l1)

    # calculate velocities using exponential weighted average
    velos = []
    weights = []
    l0s = _data['first']['lines']
    for i in range(1,l0s.shape[0]):
        velos.append(np.array(
                np.sqrt(np.sum((l0s[i][0:2]-l0s[i-1][0:2])**2))/(l0s[i][2]-l0s[i-1][2])
            ))
        weights.append((l0s[i][2]-l0s[i-1][2]) * (i**2))
    if arg['using_2_lines']:
        l1s = _data['second']['lines']
        for i in range(1,l1s.shape[0]):
            velos.append(
                    np.sqrt(np.sum((l1s[i][0:2]-l1s[i-1][0:2])**2))/(l1s[i][2]-l1s[i-1][2])
                )
            weights.append((l1s[i][2]-l1s[i-1][2]) * (i**2))
    velos = np.array(velos)
    v = np.average(velos, weights=np.array((
        weights
    )))
    
    d = v * ((_data['second']['lines'][0][2] + ts1) - (_data['first']['lines'][-1][2] + ts0))
    vd = d * (l0 / math.sqrt((l0*l0).sum()))
    vector_origin = vd + e0 - rot_l1[0][0:2]
    
    return Output(alpha, theta, vector_origin)

def ExponentialWeightedAvg3(_data, **arg):
    # _data:
    #   env
    #   subject
    #   first (line on first device, scaled by self.alpha)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin
    
    #set default args
    for a in func_args:
        if a not in arg.keys():
            arg[a] = False
    alpha = 1
    theta = 0
    vector_origin = np.ndarray([0,0])

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
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_l1 = []
    for l in _data['second']['lines']:
        rot_l1.append(np.append(getRotated(l[0:2], theta), l[2]))
    rot_l1 = np.array(rot_l1)

    # calculate velocities using exponential weighted average
    velos = []
    weights = []
    l0s = _data['first']['lines']
    for i in range(1,l0s.shape[0]):
        velos.append(np.array(
                np.sqrt(np.sum((l0s[i][0:2]-l0s[i-1][0:2])**2))/(l0s[i][2]-l0s[i-1][2])
            ))
        weights.append((l0s[i][2]-l0s[i-1][2]) * (i**3))
    velos = np.array(velos)
    v = np.average(velos, weights=np.array((
        weights
    )))
    
    d = v * ((_data['second']['lines'][0][2] + ts1) - (_data['first']['lines'][-1][2] + ts0))
    vd = d * (l0 / math.sqrt((l0*l0).sum()))
    vector_origin = vd + e0 - rot_l1[0][0:2]
    
    return Output(alpha, theta, vector_origin)
def ExponentialWeightedAvg4(_data):
    # _data:
    #   env
    #   subject
    #   first (line on first device, scaled by self.alpha)
    #   second (line on second device)

    # output: 
    #   alpha
    #   delta_theta
    #   vector_origin
    alpha = 1
    theta = 0
    vector_origin = np.ndarray([0,0])

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
    
    # get delta_theta
    theta = getAngleDiff(l0, l1)
    
    # rotate using theta
    rot_l1 = []
    for l in _data['second']['lines']:
        rot_l1.append(np.append(getRotated(l[0:2], theta), l[2]))
    rot_l1 = np.array(rot_l1)

    # calculate velocities using exponential weighted average
    velos = []
    weights = []
    l0s = _data['first']['lines']
    for i in range(1,l0s.shape[0]):
        velos.append(np.array(
                np.sqrt(np.sum((l0s[i][0:2]-l0s[i-1][0:2])**2))/(l0s[i][2]-l0s[i-1][2])
            ))
        weights.append((l0s[i][2]-l0s[i-1][2]) * (i**4))
    velos = np.array(velos)
    v = np.average(velos, weights=np.array((
        weights
    )))
    
    d = v * ((_data['second']['lines'][0][2] + ts1) - (_data['first']['lines'][-1][2] + ts0))
    vd = d * (l0 / math.sqrt((l0*l0).sum()))
    vector_origin = vd + e0 - rot_l1[0][0:2]
    
    return Output(alpha, theta, vector_origin)



