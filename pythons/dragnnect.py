# Connect devices using lines
import math
class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, _vec):
        return Vector3(self.x + _vec.x, self.y + _vec.y, self.z + _vec.z)
    def __mul__(self, _vec):
        if (type(_vec) == float):
            return Vector3(self.x*_vec, self.y*_vec, self.z*_vec)
        elif (type(_vec) == Vector3):
            return Vector3(self.x * _vec.x, self.y * _vec.y, self.z * _vec.z)
    def __str__(self):
        return str((self.x, self.y, self.z))
        #return "(" + str(self.x) + ", " + str(self.y) + ")"
    def __repr__(self):
        return self.__str__()
    def getRotated2d(self, _rad):
        x2 = math.cos(_rad) * self.x - math.sin(_rad) * self.z
        z2 = math.sin(_rad) * self.x + math.cos(_rad) * self.z
        return Vector3(x2, self.y, z2)
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
    def getFloats(self):
        return [self.x, self.y]
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
    def __init__(self, _id):
        self.device_index = _id
        self.timeDelta = 0
        self.timestamp = 0 #server timestamp
        self.startPoint = Point(0, 0)
        self.endPoint = Point(0, 0)
    def set(self, startPoint, endPoint, timeDelta, timestamp):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.timeDelta = timeDelta
        self.timestamp = timestamp
class DeviceArrangement:
    def __init__(self, _id):
        self.device_id = _id
        self.pos = Vector3()
        self.up = Vector3() # Up vector of device
        self.rot = Vector3() # Rotation vector of device
        self.width = 0
        self.height = 0
        self.timestamp = 0
    def __str__(self):
        ret = ""
        ret += "Device_id: " + str(self.device_id)
        ret += "\nSize: " + str(self.width) + ", " + str(self.height)
        ret += "\nTimestamp: " + str(self.timestamp)
        ret += "\nPosition: " + str(self.pos.x) + ", " + str(self.pos.y) + ", " + str(self.pos.z)
        ret += "\nRotation: " + str(self.rot.x) + ", " + str(self.rot.y) + ", " + str(self.rot.z)
        return ret
    def __repr__(self):
        return self.__str__()
    def setDeviceSize(self, _w, _h):
        if self.width == 0:
            self.width = _w
            self.height = _h
        elif (_w == 0) & (_h == 0):
            self.width = 0
            self.height = 0
    def get2dPoints(self):
        p0 = Point(self.pos.x, self.pos.z)
        p1 = p0 + Point(self.width, 0).getRotated(self.rot.z)
        p2 = p0 + Point(0, self.height).getRotated(self.rot.z)
        p3 = p0 + Point(self.width, self.height).getRotated(self.rot.z)
        return [p0.getFloats(), p1.getFloats(), p3.getFloats(), p2.getFloats()]

def calcUsingLines(_pre_line, _next_line):
    # pre_line을 기준으로 next_line device의 rotation, position 리턴.
    # 기준 Rotation (initialized): (0, 0, 0)
    v1 = Point.getDistance(_pre_line.startPoint, _pre_line.endPoint) / _pre_line.timeDelta
    #v2 = Point.getDistance(_next_line.startPoint, _next_line.endPoint) / _next_line.timeDelta
    vm = v1
    #
    tmp = _pre_line.endPoint - _pre_line.startPoint
    tmpUnitVector = tmp / tmp.getLength()
    # calc radian
    r1 = Point.getRadian(_pre_line.startPoint, _pre_line.endPoint)
    r2 = Point.getRadian(_next_line.startPoint, _next_line.endPoint)
    ret = dict()
    ret['rot'] = Vector3(0, 0, r1 - r2)
    #
    rotatedSP = _next_line.startPoint.getRotated(ret['rot'].z)
    distVector = tmpUnitVector * (vm * (_next_line.timestamp - _pre_line.timestamp))
    tmpPos = _pre_line.endPoint + distVector - rotatedSP
    ret['pos'] = Vector3(tmpPos.x, 0, tmpPos.y)
    return ret #return Point object of 'next' device.

def getScalefactor(_pre_line, _next_line):
    v1 = Point.getDistance(_pre_line.startPoint, _pre_line.endPoint) / _pre_line.timeDelta
    r = (v1 * _next_line.timeDelta) / Point.getDistance(_next_line.startPoint, _next_line.endPoint)
    return r

def setUsingLines(_devs, _lines):
    for i in range(0, len(_lines), 2):
        ret = calcUsingLines(_lines[i], _lines[i+1])
        _devs[_lines[i + 1].device_index].pos = \
            ret['pos'] + _devs[_lines[i].device_index].pos
        _devs[_lines[i + 1].device_index].rot = \
            ret['rot'] + _devs[_lines[i].device_index].rot

# Calculate with scaling factor.
def setUsingLines2(_devs, _lines):
    for i in range(0, len(_lines), 2):
        r = getScalefactor(_lines[i], _lines[i+1])
        for j in range(i+1, len(_lines)):
            if (_lines[j].device_index == _lines[i+1].device_index):
                _lines[j].startPoint *= r
                _lines[j].endPoint *= r
        ret = calcUsingLines(_lines[i], _lines[i+1])
        _devs[_lines[i + 1].device_index].width *= r
        _devs[_lines[i + 1].device_index].height *= r
        _devs[_lines[i + 1].device_index].pos = \
            ret['pos'].getRotated2d(_devs[_lines[i].device_index].rot.z) + _devs[_lines[i].device_index].pos
        _devs[_lines[i + 1].device_index].rot = \
            ret['rot'] + _devs[_lines[i].device_index].rot
s1 = Point(3, 3)
e1 = Point(3, 6) # dis = 3
l1 = LineData(0)
l1.set(s1, e1, 3, 3) # 0.5 second

s2 = Point(3, 3)
e2 = Point(6, 3) # degree with dev 1 = 90`
l2 = LineData(1)
l2.set(s2, e2, 3, 6)
l = []
l.append(l1)
l.append(l2)

d1 = DeviceArrangement(1)
d1.setDeviceSize(5, 6)
d2 = DeviceArrangement(2)
d2.setDeviceSize(10, 7)
d = []
d.append(d1)
d.append(d2)
setUsingLines(d, l)

print(d1)
print(d2)
arr1 = d1.get2dPoints()
print(arr1)
arr2 = d2.get2dPoints()
print(arr2)