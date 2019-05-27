# 실험 번호, 실험 환경 번호, 사용자 고유 이름(room number), \
# 시작 장치 번호, 시작 장치 서버 도달 시간, 시작 직선 정보(x, y, timestamp(delta)) 10개, \
# 끝 장치 번호, 끝 장치 서버 도달 시간, 끝 직선 정보(x, y, timestamp(delta))


#{'1': [[[0, 0], [1120.0, 0.0], [1120.0, 788.0386983289358], [0.0, 788.0386983289358]], 1, 0], '2': [[[1618.5888428851285, -191.02877813636232], [2540.7599485821715, -68.71102380729093], [2454.696445096457, 580.1340813445421], [1532.5253393994144, 457.81632701547073]], 0.8305784945014116, 0.13187129094494932]}

# 장치-직선정보:
## 1. 장치 번호
## 1.5 직선 번호
## 2. 직선 정보 서버 도달 시간
## 3. 직선 정보(x, y, timestamp(delta)) 10개
import os
import json

def createFolder(dir):
    try:
        if not(os.path.isdir(dir)):
            os.makedirs(os.path.join(dir))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

exp_seq = 0
exp_path = "./exp/"
createFolder(exp_path)
if not os.path.isfile(exp_path + "meta.txt"):
    tmp = open(exp_path + "meta.txt", "w")
    tmp.write(str(exp_seq))
    tmp.close()

tmp = open(exp_path + "meta.txt", "r")
exp_seq = int(tmp.read())
print("the present exp_seq: " + str(exp_seq))
tmp.close()
save_path = exp_path + "data/"
# save new device-line data
def saveLine(data):
    global exp_seq
    for i, d in enumerate(data):
        fn = str(exp_seq) + "-" + str(d['env']) + "-" + str(int(d['line_num'])) + "-" + str(d['subject']) + ".json"
        ret = open(save_path + fn, "w")
        ret.write(json.dumps(d, ensure_ascii=False, indent="\t"))
        ret.close()
        exp_seq += 1
    tmp = open(exp_path + "meta.txt", "w+")
    tmp.write(str(exp_seq))
    tmp.close()
