# Connect devices using lines
import math
class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    def __str__(self):
        return str((self.x, self.y))
        #return "(" + str(self.x) + ", " + str(self.y) + ")"
    def __repr__(self):
        return self.__str__()
    def set(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, _point):
        return Point(self.x + _point.x, self.y + _point.y)
    def __sub__(self, _point):
        return Point(self.x - _point.x, self.y - _point.y)
    def __mul__(self, _point):
        if type(_point) == Point:
            return Point(self.x * _point.x, self.y * _point.y)
        elif type(_point) == float:
            return Point(self.x*_point, self.y*_point)
    def __truediv__(self, _point):
        if type(_point) == Point:
            return Point(self.x/_point.x, self.y/_point.y)
        elif type(_point) == float:
            return Point(self.x/_point, self.y/_point)
    def getRotated(self, _rad):
        x2 = math.cos(_rad) * self.x - math.sin(_rad) * self.y
        y2 = math.sin(_rad) * self.x + math.cos(_rad) * self.y
        return Point(x2, y2)
    def getLength(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    def getDistance(_pnt1, _pnt2):
        tmp = _pnt2 - _pnt1
        tmp = tmp * tmp
        return math.sqrt(tmp.x + tmp.y)
    def getRadian(_pnt1, _pnt2):
        tmp = _pnt2 - _pnt1
        return math.atan2(tmp.y, tmp.x) + math.pi



class LineData:
    def __init__(self):
        self.timeDelta = 0
        self.startPoint = Point(0, 0)
        self.endPoint = Point(0, 0)
    def set(self, startPoint, endPoint, timeDelta):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.timeDelta = timeDelta

class DeviceArrangement:
    def __init__(self, _id):
        self.device_id = _id
        self.pos = Vector3()
        self.up = Vector3() # Up vector of device
        self.rot = Vector3() # Rotation vector of device
        self.line = LineData()
        self.width = 0
        self.height = 0
    def __str__(self):
        ret = ""
        ret += "Position: " + str(self.pos.x) + ", " + str(self.pos.y) + ", " + str(self.pos.z)
        ret += "\nRotation: " + str(self.rot.x) + ", " + str(self.rot.y) + ", " + str(self.rot.z)
        return ret
    def __repr__(self):
        return self.__str__()
    def setDeviceSize(self, _w, _h):
        self.width = _w
        self.height = _h
    def setDeviceId(self, _id):
        self.device_id = _id
    def setLineData(self, _startPoint, _endPoint, _timeDelta):
        self.line.set(_startPoint, _endPoint, _timeDelta)   
    def calcUsingLine(self, _line, _delta):
        # 자기를 기준으로 상대 디바이스의 rotation, position 리턴.
        # 기준 Rotation (initialized): (0, 0, 0)
        v1 = Point.getDistance(self.line.startPoint, self.line.endPoint) / self.line.timeDelta
        v2 = Point.getDistance(_line.startPoint, _line.endPoint) / _line.timeDelta
        vm = (v1 + v2) / 2
        #
        tmp = self.line.endPoint - self.line.startPoint
        tmpUnitVector = tmp / tmp.getLength()
        # calc radian
        r1 = Point.getRadian(self.line.startPoint, self.line.endPoint)
        r2 = Point.getRadian(_line.startPoint, _line.endPoint)
        retR = Vector3(self.rot.x, self.rot.y, self.rot.z + (r1 - r2))
        #
        rotatedSP = _line.startPoint.getRotated(retR.z)
        distVector = tmpUnitVector * (vm * _delta)
        ret = self.line.endPoint + distVector - rotatedSP
        return [retR, ret] #return Point object of another device.
    def get2dPoints(self):
        p0 = Point(self.pos.x, self.pos.z)
        p1 = p0 + Point(self.width, 0).getRotated(self.rot.z)
        p2 = p0 + Point(0, self.height).getRotated(self.rot.z)
        p3 = Point(p1.x, p2.y)
        return [p0, p1, p2, p3]
    def setUsingLine(_pre_dev, _next_dev, _delta):
        [r, p] = _pre_dev.calcUsingLine(_next_dev.line, _delta)
        _next_dev.rot = r
        _next_dev.pos.x += p.x
        _next_dev.pos.z += p.y

        
        


# TEST DATA
s1 = Point(3, 3)
e1 = Point(3, 6) # dis = 3
l1 = LineData()
l1.set(s1, e1, 3) # 0.5 second

s2 = Point(3, 3)
e2 = Point(6, 3) # degree with dev 1 = 90`
l2 = LineData()
l2.set(s2, e2, 3)


d1 = DeviceArrangement(1)
d1.line = l1
d1.setDeviceSize(5, 3)
d2 = DeviceArrangement(2)
d2.line = l2
d2.setDeviceSize(10, 7)

DeviceArrangement.setUsingLine(d2, d1, 6)

print(d1)
print(d2)
arr1 = d1.get2dPoints()
print(arr1)
arr2 = d2.get2dPoints()
print(arr2)