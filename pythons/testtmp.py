import math
x = (1,0)
a = (30, 30)
b = (45, 45)
t = (b[0]-a[0], b[1]-a[1])


def cal(t):
    tmpt = math.atan2(t[1], t[0])
    tmp1 = x[0]*t[1] - x[1]*t[0] 
    tmp2 = math.sqrt(x[0]*x[0] + x[1]*x[1]) * \
        math.sqrt(t[0]*t[0] + t[1]*t[1])
    tmps = math.asin(tmp1/tmp2) 
    print(tmpt)
    print(tmpt/math.pi*180.0)
    print(tmps)
    print(tmps/math.pi*180.0)

cal(t)