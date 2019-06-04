import shutil as sh 
import os


_route = './exp/data/'
dst = './exp/expd/'
fileList = (os.listdir(_route))
isit = (os.listdir(dst))
c = 0
a = 0
for i, r in enumerate(fileList):
    if (r in isit):
        print(r + "  -  already copied.")
        a += 1
    else:
        print("Copying..." + r)
        sh.copyfile(_route + r, dst + r)
        c += 1
print()
print(str(c) + " copied!")
