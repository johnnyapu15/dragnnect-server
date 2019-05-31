from flask import Flask, request, \
render_template, jsonify, session, \
json, redirect, url_for, flash
import logging
import flask_socketio as si
from datetime import datetime

#import pythons.dragnnect-exp as dragnnectExp 
from pythons.dragnnect_exp import *
# from pythons.dragnnect import *
from pythons.fileio import *

app = Flask(__name__)
app.secret_key = 'the random string'
socketio = si.SocketIO(app, manage_session=False)



# GLOBAL VAR
room = dict() # Device object list of room


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
        room[id_str]['2d_demo'] = [0,0,False]
        room[id_str]['devices'] = dict()
        room[id_str]['sequence'] = 0
        room[id_str]['count'] = 0
        room[id_str]['lines'] = []
    room[id_str]['count'] += 1
    session['device_id'] = str(room[id_str]['sequence'])
    room[id_str]['sequence'] += 1
    dev_id = session['device_id']
    room[id_str]['devices'][dev_id] = DeviceArrangement(dev_id)
    #print("Index: " + len(room[id_str]))
    return redirect(url_for('room_func', id = id_str))
    #return render_template("canvas.html", count = room_count[id_str], room_id = id_str)

@app.route('/room/<id>', methods=['POST', 'GET'])
def room_func(id):
    id_str = str(id)
    if 'device_id' in session.keys():
        # 이전에 접속한 기기가 재접속할 경우
        idx = str(list(room[id_str]['devices'].keys()).index(session['device_id']))
        session['device_id'] = idx
        return render_template("canvas.html", count = str(room[id_str]['count']), room_id = id_str, idx = session['device_id'])
    else:
        return render_template("roomDoor.html")

@socketio.on('join')
def join_room():
    id = session['room_id']
    sid = str(request.sid)
    id_str = str(id)
    si.join_room(id_str)
    print("---Log: " + str(session))
    print(room)
    # print(si.rooms())
    # print("Joining into " + id_str + "...")
    # print("SID: " + str(sid))
    # print("Index: " + str(room_count[id_str]))
    si.emit('update', {'count':room[id_str]['count']}, room = id_str)
    #si.emit('redirect', {'url':url_for('room_func', id = id_str)})

@socketio.on('disconnect')
def disc():
    print("***********************DISCONNECTED ON SOCKETIO***************************")

@socketio.on('leave')
def quit_callback():
    id = str(session['room_id'])
    print("device " + str(session['device_id']) + ": QUIT from " + id)
    room[id]['count'] -= 1
    if room[id]['count'] == 0:
        del room[id]['devices']
        #del room_lines[id]
        del room[id]['lines']
        del room[id]['sequence']
    else:
        del room[id]['devices'][session['device_id']]
        try:
            #for idx, line in enumerate(room_lines[id]):
            for idx, line in enumerate(room[id]['lines']):
                if (line.device_index == session['device_id']):
                    #del room_lines[id][idx]
                    del room[id]['lines'][idx]
                    if (idx % 2) == 0:
                        #del room_lines[id][idx]
                        del room[id]['lines'][idx]
                    else:
                        #del room_lines[id][idx - 1]
                        del room[id]['lines'][idx - 1]
        except IndexError as e:
            print(e)
    si.leave_room(id)
    
    si.emit('update', {'count':room[id]['count']}, room = id)

@app.route('/room/callback', methods=['POST', 'GET'])
def callback():
    print(request.json)
    return str(request.json)

@app.route('/test')
def testsite():
    return render_template("maps.html")


@socketio.on('ntp_start')
def ntp_0():
    print('ntp...0')
    t0 = int(datetime.utcnow().timestamp() * 1000)
    si.emit('ntp_0')
    room[session['room_id']]['devices'][session['device_id']].ntpTimes = t0


@socketio.on('ntp_1')
def ntp_1(t1):
    print('ntp...1')
    t2 = int(datetime.utcnow().timestamp() * 1000)
    t0 = room[session['room_id']]['devices'][session['device_id']].ntpTimes
    delay = ((t1 - t0) + (t2 - t1)) / 2
    delta = t1 - t0 - delay
    si.emit('ntp_delta', delta)
    room[session['room_id']]['devices'][session['device_id']].ntpDelay = delay
    print("Delta for " + str(session['device_id']) +": " + str(delta))

@socketio.on('reset_lines')
def reset_lines():
    room_id = session['room_id']
    for key, dev in room[room_id]['devices'].items():
        dev.setDeviceSize(0, 0)
    #room_lines[room_id] = []
    room[room_id]['lines'] = []
    print(str(room_id) + ": reset lines...")

@socketio.on('kill_room')
def kill_room():
    si.emit("room_kill", room=session['room_id'])
    id = session['room_id']
    del room[id]['devices']
    #del room_lines[session['room_id']]
    del room[id]['lines']
    del room[id]['sequence']
    del room[id]
    print("room killed.")
def devLineToData(_meta, _devs, _lines):
    ret = []
    for i in range(0, len(_lines), 2):
        # devname, lineseq, servertime, linedata
        # _devs[_lines[i].device_index].device_name
        # i
        # _lines[i].timestamp
        # _lines[i].pnts 
        ret.append(
            {
                'env': _meta[0],
                'subject': _meta[1],
                'line_num': int(i / 2),
                'first':{
                    'dev_index': _lines[i].device_index,
                    'dev_info':     _devs[_lines[i].device_index].device_name,
                    'width': _devs[_lines[i].device_index].width,
                    'height': _devs[_lines[i].device_index].height,
                    'timestamp':    _lines[i].timestamp,
                    'lines':        _lines[i].lines
                },
                'second':{
                    'dev_index': _lines[i+1].device_index,
                    'dev_info':    _devs[_lines[i+1].device_index].device_name,
                    'width': _devs[_lines[i+1].device_index].width,
                    'height': _devs[_lines[i+1].device_index].height,
                    'timestamp':   _lines[i+1].timestamp,
                    'lines':       _lines[i+1].lines
                }
            }
        )
    return ret
# @socketio.on('device_update')
# def dev_update(data):
#     print(session['device_id'])
#     print(room)
#     #dpmm = data['dpi_x'] / 25.4
#     #dpv = dpmm / 5
#     #print("DPI: " + str(data['dpi_x']) + " ... dpmm: " + str(dpmm))
#     room_id = session['room_id']
#     count = room[room_id]['count']
#     dev_id = int(session['device_id'])
#     pnts = data['11pnts']
#     s0 = Point(pnts[0][0], pnts[0][1])
#     e0 = Point(pnts[-1][0], pnts[-1][1])
#     #s0 /= dpv
#     #e0 /= dpv
#     l0 = LineData(dev_id)
#     l0.set(s0, e0, pnts[-1][2] - pnts[0][2], data['start_time'])
#     l0.lines = pnts
#     room[room_id]['devices'][dev_id].setDeviceSize(data['width'], data['height'])
#     room[room_id]['devices'][dev_id].device_name = session['dev_info']
#     #room[room_id][dev_id].setDeviceSize(data['width'] / dpv, data['height'] / dpv)

#     #room_lines[room_id].append(l0)
#     room[room_id]['lines'].append(l0)

#     ret = dict()
#     #if 2 * count - 2 <= len(room_lines[room_id]):
#     if 2 * count - 2 <= len(room[room_id]['lines']):
#         room[room_id]['lines'] = room[room_id]['lines'][0:(2*count-2)]
#         # Init
#         for key, dev in room[room_id]['devices'].items():
#             if (key!='2d_demo'):
#                 dev.rot = Vector3()
#                 dev.pos.x = 0
#                 dev.pos.z = 0
#                 dev.alpha = 1
#         LD = devLineToData([
#                 room[room_id]['expNum'],
#                 room_id
#             ], 
#             room[room_id]['devices'], room[room_id]['lines'])
#         saveLine(LD)
#         # Calculate
#         #setUsingLines(room[room_id], room_lines[room_id])
#         #setUsingLines2(room[room_id]['devices'], room_lines[room_id])
#         setUsingLines2(room[room_id]['devices'], room[room_id]['lines'])
#         for key, dev in room[room_id]['devices'].items():
#             if (key!='2d_demo'):
#                 ret[str(dev.device_id)] = \
#                     [dev.get2dPoints(), dev.alpha, dev.rot.z]
#         print("drawing...")
#         print(LD)
#         print(ret)
#         si.emit('draw', ret, room=room_id)
#         # Reset
#         for key, dev in room[room_id]['devices'].items():
#             if (key!='2d_demo'):
#                 dev.setDeviceSize(0, 0)
#         #room_lines[room_id] = []
#         room[room_id]['lines'] = []
#     elif 2 * count - 2 > len(room[room_id]['lines']):
#         # Listening,,,
#         return
#     else:
#         # TODO: draw or reset
#         for key, dev in room[room_id]['devices'].items():
#             if (key!='2d_demo'):
#                 dev.setDeviceSize(0, 0)
#         room[room_id]['lines'] = []
#         return

@socketio.on('device_update')
def dev_update2(data):
    print(session['device_id'])
    print(room)
    room_id = session['room_id']
    count = room[room_id]['count']
    dev_id = str(session['device_id'])
    pnts = data['11pnts']
    l0 = LineData(dev_id)
    l0.set(pnts, data['start_time'])
    room[room_id]['devices'][dev_id].setDeviceSize(data['width'], data['height'])
    room[room_id]['devices'][dev_id].device_name = session['dev_info']
    room[room_id]['lines'].append(l0)

    ret = dict()
    if 2 * count - 2 <= len(room[room_id]['lines']):
        room[room_id]['lines'] = room[room_id]['lines'][0:(2*count-2)]
        # Init
        for key, dev in room[room_id]['devices'].items():
            dev.init()
        LD = devLineToData(
            [
                room[room_id]['expNum'],
                room_id
            ], 
            room[room_id]['devices'], room[room_id]['lines']
        )
        saveLine(LD)
        for i, l in enumerate(LD):
            l['first']['lines'] = np.array(l['first']['lines'])
            l['second']['lines'] = np.array(l['second']['lines'])
        # Calculate
        for i, l in enumerate(LD):
            print(l)
            i0 = str(l['first']['dev_index'])
            i1 = str(l['second']['dev_index'])
            output = heuristic_basic(l)
            room[room_id]['devices'][i0].link(
                room[room_id]['devices'][i1],
                output
            )
        for key, dev in room[room_id]['devices'].items():
            ret[str(dev.device_id)] = \
                [dev.get2dPoints(), dev.alpha, dev.rot[1]]
        print("drawing...")
        print(LD)
        print(ret)
        print(room[room_id]['devices'])
        si.emit('draw', ret, room=room_id)
        # Reset
        for key, dev in room[room_id]['devices'].items():
            dev.setDeviceSize(0, 0)
        room[room_id]['lines'] = []
    elif 2 * count - 2 > len(room[room_id]['lines']):
        # Listening,,,
        return
    else:
        # TODO: draw or reset
        for key, dev in room[room_id]['devices'].items():
            dev.setDeviceSize(0, 0)
        room[room_id]['lines'] = []
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
    id_str = str(session['room_id'])
    room[id_str]['2d_demo'][0] = data[0]
    room[id_str]['2d_demo'][1] = data[1]
    print("pnt demo..." + str(room[id_str]['2d_demo']))
    si.emit('2d-pnt-draw', room[id_str]['2d_demo'], room=session['room_id'], include_self=False)
    #si.broadcast.to(session['room_id']).emit('2d-pnt-draw', room[id_str]['2d_demo'])
    # DeviceArrangement.setUsingLine(room[room_id][0], room[room_id][1])
@socketio.on('sendingExpNum')
def setExpNum(data):
    print("exp: " + str(data))
    room[session["room_id"]]["expNum"] = data
    si.emit('flash', "Experiment number is " + str(room[session["room_id"]]["expNum"]))
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    #app.run(host='0.0.0.0')
    socketio.run(app, host='0.0.0.0')
