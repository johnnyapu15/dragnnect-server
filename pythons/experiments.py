import dragnnect_exp as dr 
import numpy as np
import os
import matplotlib.pyplot as plt
import dragnnect_nn as nn

# fileList = (os.listdir(fileRoute))
# print(fileList)
# routes = fileList
# e = 'default'
# l = '2'
# s = '0'
# # for i in range(39, 41):
# #     routes.append(
# #         'exp/data/' + 
# #         str(i) + "-" +
# #         e + "-" + 
# #         l + "-" +
# #         s + ".json"
# #     )

def printExp(_json, _func, _print=False):
    env = _json['env']
    line_num = _json['line_num']
    output = _func(_json)
    d, t = getTrueDistanceAndTime(_json)
    output.t_v = d / t
    output.t0 = _json['first']['lines'][-1][2]
    output.t1 = _json['second']['timestamp'] - _json['first']['timestamp']
    true = envs[env]
    mse = dr.getMSEVector(output, true)
    #_devs[0].link(_devs[1], output)
    if _print:
        print("")
        print("function: " + _func.__qualname__)
        print("Output: \n" + str(output))
        # print(" " + str(_devs[0].get2dPoints()))
        # print(" " + str(_devs[1].get2dPoints()))
        print(mse)
        print("----------------------------")
    return mse, output

def loadJsonsFromFolder(_route):
    fileList = [f for f in os.listdir(_route) if os.path.isfile(_route + f)]
    jsons = dict()
    jsons_name = dict()
    for i, r in enumerate(fileList):
        js, devs = dr.jsonToData(fileRoute + r)
        env = js['env']
        jsons_name[r] = js
        if env not in jsons.keys():
            jsons[env] = []
        jsons[env].append(js)
        jsons[env][-1]['filename'] = r
    rows = dict()
    for e in jsons.keys():
        rows[e] = len(jsons[e])
    return jsons, rows, jsons_name

def getMetaData(js, r):
    # env - number
    # time - (min, max, mean, stdv)
    ret = ""
    # env
    ret += "Environments: \n"
    for i, e in enumerate(r.keys()):
        ret += e + " --- " + str(r[e]) + ' rows\n'
    ret += '\n'
    
    # time meta data
    t = dict()
    for i, e in enumerate(js.keys()):
        t[e] = np.zeros((2, r[e]))
        for j in range(r[e]):
            t[e][0][j] = js[e][j]['first']['lines'][-1][2]
            t[e][1][j] = js[e][j]['second']['lines'][-1][2]
    ret += "Meta data of timestamps (min, max, mean, stdv):"
    for i, e in enumerate(r.keys()):
        ret += e + " -----\n"
        ret += " [" + str(t[e][0].min()) + ", " + str(t[e][0].max()) + ", " + str(t[e][0].mean()) + ", " + str(t[e][0].std()) + "\n"
        ret += " [" + str(t[e][1].min()) + ", " + str(t[e][1].max()) + ", " + str(t[e][1].mean()) + ", " + str(t[e][1].std()) + "\n"
    return ret
## For training

def loadTrainDataFromFolder(_route):
    fileList = [f for f in os.listdir(_route) if os.path.isfile(_route + f)]
    data = dict()
    for i, r in enumerate(fileList):
        js, devs = dr.jsonToData(fileRoute + r)
        env = js['env']
        if env not in data.keys():
            data[env] = []
        data[env].append(dr.getVelos(js))
    rows = dict()
    for e in data.keys():
        rows[e] = len(data[e])
    return data, rows
def getTrueDistanceAndTime(_json):
    # v_d = v_o - e0 + s1
    global envs
    true = envs[_json['env']]
    vd = np.array(true.vo) - _json['first']['lines'][-1][0:2] + _json['second']['lines'][0][0:2]
    dist = np.sqrt(np.sum(vd**2))
    time = _json['second']['timestamp'] - (_json['first']['timestamp'] + _json['first']['lines'][-1][2])
    return dist, time

def trainExp(_json, _trainFunc):
    global envs
    env = _json['env']
    line_num = _json['line_num']
    #output = _func(_json)
    #_devs[0].link(_devs[1], output)
    print("")
    print("function: " + _func.__qualname__)
    print("Output: \n" + str(output))
    # print(" " + str(_devs[0].get2dPoints()))
    # print(" " + str(_devs[1].get2dPoints()))
    true = envs[env]
    mse = dr.getMSEVector(output, true)
    print(mse)
    print("----------------------------")
    return mse, output


def plotVelos(_output):
    v = np.transpose(_output.velos)
    g = sorted(v, key=lambda e: e[1])
    g = np.transpose(g)
    trues = [
        [_output.t0, _output.t1],
        [_output.t_v, _output.t_v]
    ]
    plt.plot(g[1], g[0], trues[0], trues[1], 'r-')
    plt.show()


def checkData(_route):
    fileList = [f for f in os.listdir(_route) if os.path.isfile(_route + f)]
    data = dict()
    ret = ''
    for i, r in enumerate(fileList):
        js, devs = dr.jsonToData(fileRoute + r)
        ret += r
        ret += " " + str(js['second']['timestamp'] - js['first']['timestamp'])
        print(ret)
        ret = ''
##################################
envs = dr.jsonToEnv('exp/envs.json')
fileRoute = "exp/expd/"
outputs = []
trues = []
col = ['alpha', 'theta', 'x_v', 'y_v']
algos = [
    dr.heuristic_basic,
    dr.sumDist,
    dr.simpleAvg,
    dr.weightedAvg,
    dr.ExponentialWeightedAvg2,
    dr.ExponentialWeightedAvg3,
    dr.simpleRegression
    ]
MSEs = dict()
Outputs = dict()
velos = dict()
jsons, rows, jsons_name = loadJsonsFromFolder(fileRoute)
j_keys = list(jsons.keys())
r = 0
for e in j_keys:
    r += rows[e]
print(getMetaData(jsons, rows))
#checkData(fileRoute)


expbasic = False
deeplearn = True
getCoef = True
l0 = 10
l1 = 5
## Exp basic
if expbasic:
    for e in j_keys:
        MSEs[e] = dict()
        Outputs[e] = dict()
        velos[e] = []
        for s in algos:
            MSEs[e][s.__qualname__] = np.zeros((rows[e],4))
            Outputs[e][s.__qualname__] = []
    for i, e in enumerate(j_keys):
        js_e = jsons[e]
        for i_j, js in enumerate(js_e):
            #print("----------------------------------")
            env = js['env']
            #line_num = js['line_num']
            #print("env: " + env)
            #print("line: " + str(line_num))
            # velos[e].append(list(dr.getVelos(js)[0]))
            # velos[e][-1].append(np.mean(velos[e][-1][0:5]))
            # velos[e][-1].append(np.mean(velos[e][-1][5:10]))
            # velos[e][-1].append(np.mean(velos[e][-1]))
            d, t = getTrueDistanceAndTime(js)
            # velos[e][-1].append(d/t)
            # velos[e][-1] = np.array(velos[e][-1])
            tmp = dr.jsonToTrain(js, l0, l1)
            
            velos[e].append(np.append(tmp, d/t))
            for s in algos:
                MSEs[e][s.__qualname__][i_j], o = printExp(js, s)
                Outputs[e][s.__qualname__].append(o)
        velos[e] = np.array(velos[e])
    print(MSEs)
    for e in j_keys:
        print("ENV: " + e)
        print("Velos, shape=" + str(velos[e].shape))
        print(velos[e])
        ## Corrcoef: velos of first device, velos of second device, mean of d1, mean of d2, mean, true
        print("Coef:")
        print(np.corrcoef(velos[e], rowvar=False))
        for s in algos:
            print("   " + s.__qualname__)
            print("   " + str(np.mean(MSEs[e][s.__qualname__],0)))
            print("   " + str(np.std(MSEs[e][s.__qualname__], 0)))
if getCoef:
    for e in j_keys:
        velos[e] = []
    for i, e in enumerate(j_keys):
        js_e = jsons[e]
        for i_j, js in enumerate(js_e):
            d, t = getTrueDistanceAndTime(js)
            tmp = dr.jsonToTrain(js, l0, l1)    
            for i, v in enumerate(tmp[:-1]):
                tmp[i] *= 1
            velos[e].append(np.append(tmp, d/t))
        velos[e] = np.array(velos[e])
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)
    for e in j_keys:
        print("ENV: " + e)
        print("Velos, shape=" + str(velos[e].shape))
        ## Corrcoef: velos of first device, velos of second device, mean of d1, mean of d2, mean, true
        print("Coef:")
        cc = np.corrcoef(velos[e], rowvar=False)
        print(cc[-1])

# for i, js in enumerate(jsons):
#     print("----------------------------------")
    
#     env = js['env']
#     line_num = js['line_num']
#     print("env: " + env)
#     print("line: " + str(line_num))
#     for s in algos:
#         MSEs[env][s.__qualname__][i] = printExp(devs, js, s)

def getOutputFromVelo(_json, _velo):
    v1 = _json['first']['lines'][-1][0:2] - _json['first']['lines'][0][0:2]
    v1d = np.sqrt((v1 ** 2).sum())
    vu = v1 / v1d 
    dt = _json['second']['timestamp'] - _json['first']['timestamp'] - _json['first']['lines'][-1][2]
    vd = vu * _velo * dt
    return dr.Output(1, 0, vd + _json['first']['lines'][-1][0:2] - _json['second']['lines'][0][0:2])
def getExpFromMLResult(_result):
    global jsons_name, jsons, envs
    Outputs = dict()
    MSEs = dict()
    for i, e in enumerate(jsons.keys()):
        Outputs[e] = []
        MSEs[e] = []
    print(_result)
    for i, filename in enumerate(_result['keys']):
        _json = jsons_name[filename]
        velo = _result['outputs'][i]
        o = getOutputFromVelo(_json, velo)
        Outputs[_json['env']].append(o)
        true = envs[_json['env']]
        MSEs[_json['env']].append(dr.getMSEVector(o, true))
    for i, e in enumerate(jsons.keys()):
        print("ENV: " + e)
        print("   " + str(np.mean(MSEs[e], 0)))
        print("   " + str(np.std(MSEs[e], 0)))
    return Outputs, MSEs
# # Machine Learning
def dl():
    global jsons, j_keys
    c = l0 + l1 + 1
    # create train data
    traindata = dict()
    traindata['x'] = np.zeros((r, 2*c - 1))
    traindata['trues'] = np.zeros((r, 1))
    traindata['filename'] = []
    tmpi = 0
    for i, e in enumerate(j_keys):
        js_e = jsons[e]
        for j, js in enumerate(js_e):
            d, t = getTrueDistanceAndTime(js)
            tmp = dr.jsonToTrain(js, l0, l1)
            tmp2 = []
            for i, v in enumerate(tmp[:-1]):
                tmp2.append(v*t)
            traindata['x'][tmpi] = np.append(tmp, tmp2)
            traindata['trues'][tmpi] = d / t
            traindata['filename'].append(js['filename'])
            tmpi += 1
    dt = nn.d_data(traindata)
    dt.init(0.2) # test ratio
    net = nn.d_mlp(c*2 - 1, [64, 32], ['sigmoid', 'relu'])
    tr = nn.train(net, dt, 500, _print=True, _aim=10)
    getExpFromMLResult(tr['out'])
if deeplearn:
    dl()



    
# plotVelos(Outputs[j_keys[-1]]["simpleRegression"][-1])

