from flask import Flask, request, \
render_template, jsonify, session, \
json, redirect, url_for
import logging
import flask_socketio as si
from datetime import datetime

from pythons.dragnnect import *


app = Flask(__name__)
app.secret_key = 'the random string'
socketio = si.SocketIO(app, manage_session=False)



# GLOBAL VAR
room_count = dict()
room = dict() # Device object list of room
room_sequence = dict() # object list of room
room_lines = dict()
@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("roomDoor.html")

@app.route('/roomInit', methods=['POST'])
def roomInit():
    session['dev_info'] = str(request.form['dev_info'])
    session['user_id'] = str(request.form['id'])
    id_str = str(request.form['room_id'])
    session['room_id'] = id_str
    if not(id_str in room.keys()):
        room[id_str] = dict()
        room_sequence[id_str] = 0
        room_count[id_str] = 0
        room_lines[id_str] = []
    room_count[id_str] += 1
    session['device_id'] = room_sequence[id_str]
    room_sequence[id_str] += 1
    room[id_str][session['device_id']] = DeviceArrangement(session['device_id'])
    #print("Index: " + len(room[id_str]))
    return redirect(url_for('room_func', id = session['room_id']))
    #return render_template("canvas.html", count = room_count[id_str], room_id = id_str)

@app.route('/room/<int:id>', methods=['POST', 'GET'])
def room_func(id):
    id_str = str(id)
    if 'device_id' in session.keys():
        # print(room)
        idx = list(room[id_str].keys()).index(session['device_id'])
        # print(session['device_id'])
        # print("Insert..." + str(idx))
        session['device_id'] = idx
        return render_template("canvas.html", count = str(room_count[id_str]), room_id = id_str, idx = session['device_id'])
    else:
        return render_template("roomDoor.html")

@socketio.on('join')
def join_room(data):
    id = session['room_id']
    sid = str(request.sid)
    id_str = str(id)
    si.join_room(id_str)
    print("---Log: " + str(session))
    ntp_0()
    # print(si.rooms())
    # print("Joining into " + id_str + "...")
    # print("SID: " + str(sid))
    # print("Index: " + str(room_count[id_str]))
    si.emit('update', {'count':room_count[id_str]}, room = id_str)
    #si.emit('redirect', {'url':url_for('room_func', id = id_str)})

@socketio.on('disconnect')
def disc():
    print("***********************DISCONNECTED ON SOCKETIO***************************")

@socketio.on('leave')
def quit_callback():
    id = str(session['room_id'])
    print("device " + str(session['device_id']) + ": QUIT from " + id)
    room_count[id] -= 1
    if room_count[id] == 0:
        del room[id]
        del room_lines[id]
        del room_sequence[id]
    else:
        del room[id][session['device_id']]
        try:
            for idx, line in enumerate(room_lines[id]):
                if (line.device_index == session['device_id']):
                    del room_lines[id][idx]
                    if (idx % 2) == 0:
                        del room_lines[id][idx]
                    else:
                        del room_lines[id][idx - 1]
        except IndexError as e:
            print(e)
    si.leave_room(id)
    
    si.emit('update', {'count':room_count[id]}, room = id)

@app.route('/room/callback', methods=['POST', 'GET'])
def callback():
    print(request.json)
    return str(request.json)

@app.route('/test')
def testsite():
    return render_template("test.html")

def ntp_0():
    print('ntp...0')
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    t0 = int("%s%03d" % (dt, int(micro) / 1000))
    room[session['room_id']][session['device_id']].ntpTimes = []
    room[session['room_id']][session['device_id']].ntpTimes.append(t0)
    si.emit('ntp_0')



@socketio.on('ntp_1')
def ntp_1(t1):
    print('ntp...1')
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    t2 = int("%s%03d" % (dt, int(micro) / 1000))
    t0 = room[session['room_id']][session['device_id']].ntpTimes[0]
    delay = ((t1 - t0) + (t2 - t1)) / 2
    room[session['room_id']][session['device_id']].ntpDelay = delay
    print("Delay: " + str(delay))

@socketio.on('reset_lines')
def reset_lines():
    room_id = session['room_id']
    for key, dev in room[room_id].items():
        dev.setDeviceSize(0, 0)
    room_lines[room_id] = []
    print(str(room_id) + ": reset lines...")

@socketio.on('device_update')
def dev_update(data):
    print(session['device_id'])
    print(data)
    #dpmm = data['dpi_x'] / 25.4
    #dpv = dpmm / 5
    #print("DPI: " + str(data['dpi_x']) + " ... dpmm: " + str(dpmm))
    room_id = session['room_id']
    count = room_count[room_id]
    dev_id = int(session['device_id'])
    pnts = data['11pnts']
    s0 = Point(pnts[0][0], pnts[0][1])
    e0 = Point(pnts[-1][0], pnts[-1][1])
    #s0 /= dpv
    #e0 /= dpv
    l0 = LineData(dev_id)
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    l0.set(s0, e0, pnts[-1][2] - pnts[0][2], int("%s%03d" % (dt, int(micro) / 1000)))
    room[room_id][dev_id].setDeviceSize(data['width'], data['height'])
    #room[room_id][dev_id].setDeviceSize(data['width'] / dpv, data['height'] / dpv)

    room_lines[room_id].append(l0)

    ret = dict()
    if 2 * count - 2 == len(room_lines[room_id]):
        # TODO: Save lines!
        # Env#_User#_Timestamp_dev1_dev2.txt
        # Init
        for key, dev in room[room_id].items():
            dev.rot = Vector3()
            dev.pos.x = 0
            dev.pos.z = 0
            dev.alpha = 1
        # Calculate
        #setUsingLines(room[room_id], room_lines[room_id])
        setUsingLines2(room[room_id], room_lines[room_id])
        for key, dev in room[room_id].items():
            ret[str(dev.device_id)] = \
                [dev.get2dPoints(), dev.alpha, dev.rot.z]
        print(ret)
        si.emit('draw', ret, room=room_id)
        # Reset
        for key, dev in room[room_id].items():
            dev.setDeviceSize(0, 0)
        room_lines[room_id] = []
    elif 2 * count - 2 > len(room_lines[room_id]):
        # Listening,,,
        return
    else:
        # TODO: draw or reset
        for key, dev in room[room_id].items():
            dev.setDeviceSize(0, 0)
        room_lines[room_id] = []
        return
@socketio.on('2d-demo')
def demo_2d():
    data = dict()
    data['lines'] = []
    for i in range(-3000, 3000, 100):
        data['lines'].append([-3000, i])
        data['lines'].append([3000, i])
        data['lines'].append([i, -3000])
        data['lines'].append([i, 3000])
    data['dl'] = []
    for i in range(-3000, 3000, 100):
        data['dl'].append([-3000, i])
        data['dl'].append([3000, i])
    si.emit('demo-2d-line', data, room=session['room_id'])
@socketio.on('2d-demo-pnt')
def demo_2d_pnt(data):
    print("pnt demo..." + str(data))
    si.emit('2d-pnt-draw', data, room=session['room_id'])
    
    # DeviceArrangement.setUsingLine(room[room_id][0], room[room_id][1])

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    #app.run(host='0.0.0.0')
    socketio.run(app, host='0.0.0.0')



# def quit_callback():
#     #id = str(data['data']['id'])
#     print("wwww")
#     # id = str(request.json['id'])
#     # idx = str(request.json['count'])
#     #print(id)
#     print(si.rooms())
#     sid = request.sid
#     id = room[request.sid]
#     #sid = str(request.json['sid'])
#     room[id].remove(sid)
#     si.leave_room(id)
#     print("Quiting..." + id)
#     return str(request.json)