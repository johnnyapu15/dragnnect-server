# 실험 번호, 실험 환경 번호, 사용자 고유 이름, 시작 장치 번호, 시작 장치 서버 도달 시간, 시작 직선 정보(x, y, timestamp(delta)) 10개, 끝 장치 번호, 끝 장치 서버 도달 시간, 끝 직선 정보(x, y, timestamp(delta))

# 장치-직선정보:
## 1. 장치 번호
## 2. 직선 정보 서버 도달 시간
## 3. 직선 정보(x, y, timestamp(delta)) 10개
import os
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

# save new device-line data
def saveLine(data):
