import json
import os


fileRoute = './exp/expd/'
fileList = (os.listdir(fileRoute))

# for f in fileList:
#     if 'add1' in f:
#         tmp = f.replace('adj1', 'D1')
#         tmp = tmp.replace('adj2', 'D2')
#         os.rename(fileRoute + f, fileRoute + tmp)

for f in fileList:
    if 'add1' in f:
        fi = open(fileRoute + f, 'r').read()
        fi = fi.replace('adj', 'D')
        tmp = open(fileRoute + f, 'w')
        tmp.write(fi)
        tmp.close()
        
        