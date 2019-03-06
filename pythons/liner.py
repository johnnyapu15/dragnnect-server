# Connect devices using lines
import math
class Vector3:
    x = 0
    y = 0
    z = 0
    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Point:
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def set(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, _point):
        return Point(self.x + _point.x, self.y + _point.y)
    def __sub__(self, _point):
        return Point(self.x - _point.x, self.y - _point.y)
    def __mul__(self, _point):
        return Point(self.x * _point.x, self.y * _point.y)
    def __truediv__(self, _point):
        if type(_point) == Point:
            return Point(self.x/_point.x, self.y/_point.y)
        elif type(_point) == int:
            return Point(self.x/_point, self.y/_point)
    def getLength(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    def getDistance(_pnt1, _pnt2):
        tmp = _pnt2 - _pnt1
        tmp = tmp * tmp
        return math.sqrt(tmp.x + tmp.y)



class lineData:
    startPoint = Point()
    endPoint = Point()
    timeDelta = 0
    def set(self, startPoint, endPoint, timeDelta):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.timeDelta = timeDelta

class deviceArrangement:
    device_id = 0
    pos = Vector3()
    up = Vector3() # Up vector of device
    line = lineData()
    def setDeviceId(self, _id):
        self.device_id = _id

    def setLineData(self, _startPoint, _endPoint, _timeDelta):
        self.line.set(_startPoint, _endPoint, _timeDelta)

    def calcUsingLine(self, _line, _delta):
        # 자기를 기준으로 상대 디바이스가 얼마나 떨어져있는 지 리턴.
        v1 = Point.getDistance(self.line.startPoint, self.line.endPoint) / self.line.timeDelta
        v2 = Point.getDistance(_line.startPoint, _line.endPoint) / _line.timeDelta
        vm = (v1 + v2) / 2
        
        tmp = self.line.endPoint - self.line.startPoint
        tmpUnitVector = tmp / tmp.getLength
        print(tmpUnitVector.getLength)
        #
        distVector = tmpUnitVector * (vm * _delta)
        ret = self.line.endPoint + distVector - _line.startPoint
        return ret
        

