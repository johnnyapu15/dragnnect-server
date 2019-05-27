import dragnnect_exp as dr 
import numpy as np
import os

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

def printExp(_json, _func):
    env = _json['env']
    line_num = _json['line_num']
    output = _func(_json)
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
    return mse

def loadJsonsFromFolder(_route):
    fileList = (os.listdir(_route))
    jsons = dict()
    for i, r in enumerate(fileList):
        js, devs = dr.jsonToData(fileRoute + r)
        env = js['env']
        if env not in jsons.keys():
            jsons[env] = []
        jsons[env].append(js)
    rows = dict()
    for e in jsons.keys():
        rows[e] = len(jsons[e])
    return jsons, rows


##################################
envs = dr.jsonToEnv('exp/envs.json')
fileRoute = "exp/test/"
outputs = []
trues = []
col = ['alpha', 'theta', 'x_v', 'y_v']
algos = [
    dr.heuristic_basic,
    dr.SimpleAvg,
    dr.WeightedAvg,
    dr.ExponentialWeightedAvg2,
    dr.ExponentialWeightedAvg3,
    dr.ExponentialWeightedAvg4
    ]
MSEs = dict()
jsons, rows = loadJsonsFromFolder(fileRoute)
for e in jsons.keys():
    MSEs[e] = dict()
    for s in algos:
        MSEs[e][s.__qualname__] = np.zeros((rows[e],4))

for i, e in enumerate(jsons.keys()):
    js_e = jsons[e]
    for i_j, js in enumerate(js_e):
        print("----------------------------------")
        env = js['env']
        line_num = js['line_num']
        print("env: " + env)
        print("line: " + str(line_num))
        for s in algos:
            MSEs[e][s.__qualname__][i_j] = printExp(js, s)
    
# for i, js in enumerate(jsons):
#     print("----------------------------------")
    
#     env = js['env']
#     line_num = js['line_num']
#     print("env: " + env)
#     print("line: " + str(line_num))
#     for s in algos:
#         MSEs[env][s.__qualname__][i] = printExp(devs, js, s)

print(MSEs)
for e in jsons.keys():
    print("ENV: " + e)
    for s in algos:
        print("   " + s.__qualname__)
        print("   " + str(np.average(MSEs[e][s.__qualname__],0)))
        print("   " + str(np.std(MSEs[e][s.__qualname__], 0)))
    

