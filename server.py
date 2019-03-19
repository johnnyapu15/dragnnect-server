from flask import Flask, request, \
render_template, jsonify, session, \
json, redirect, url_for

import flask_socketio as si
from datetime import datetime

from pythons.liner import *


app = Flask(__name__)
app.secret_key = 'the random string'
socketio = si.SocketIO(app, manage_session=False)


# GLOBAL VAR
room_count = dict()
room = dict() # Device object list of room
room_indexes = dict() # object list of room

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("roomDoor.html")

@app.route('/roomInit', methods=['POST'])
def roomInit():
    id_str = str(request.form['room_id'])
    session['room_id'] = id_str
    if not(id_str in room_count.keys()):
        room_count[id_str] = 0
    room_count[id_str] += 1
    if not(id_str in room.keys()):
        room[id_str] = []
        room_indexes[id_str] = []
    session['device_index'] = len(room[id_str])
    room[id_str].append(DeviceArrangement(session['device_index']))
    
    #print("Index: " + len(room[id_str]))
    return redirect(url_for('room_func',id = session['room_id']))
    #return render_template("canvas.html", count = room_count[id_str], room_id = id_str)

@app.route('/room/<int:id>', methods=['POST', 'GET'])
def room_func(id):
    id_str = str(id)
    return render_template("canvas.html", count = str(room_count[id_str]), room_id = id_str)

@socketio.on('join')
def join_room(data):
    print(data)
    id = session['room_id']
    sid = str(request.sid)
    id_str = str(id)
    
    si.join_room(id_str)
    print("------------------------Log-----------------------")
    print(si.rooms())
    print("Joining into " + id_str + "...")
    print("SID: " + str(sid))
    print("Index: " + str(room_count[id_str]))
    si.emit('update', {'count':room_count[id_str]}, room = id_str)
    #si.emit('redirect', {'url':url_for('room_func', id = id_str)})

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@socketio.on('disconnect')
def disc():
    print("***********************DISCONNECTED ON SOCKETIO***************************")

@socketio.on('leave')
def quit_callback():
    print("quit")
    id = str(session['room_id'])
    sid = str(request.sid)
    room_count[id] -= 1
    del room[id][session['device_index']]
    si.leave_room(id)
    si.emit('update', {'count':room_count[id]}, room = id)
    print("Quiting..." + id)

@app.route('/room/callback', methods=['POST', 'GET'])
def callback():
    print(request.json)
    return str(request.json)

@socketio.on('device_update')
def dev_update(data):
    room_id = session['room_id']
    count = room_count[room_id]

    s0 = Point(data["start_x"], data["start_y"])
    e0 = Point(data["end_x"], data["end_y"])
    l0 = LineData()
    l0.set(s0, e0, data["end_time"] - data["start_time"])
    dev = room[room_id][int(session['device_index'])]
    dev.line = l0
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    dev.timestamp = int("%s%03d" % (dt, int(micro) / 1000))
    dev.setDeviceSize(data['width'], data['height'])
    print(room)
    # room_lines[room_id].append(session['device_index'])
    # room_lines[room_id].append(l0)
    room_indexes[room_id].append(int(session['device_index']))
    ret = []
    print(count)
    print(room_indexes)
    if count == len(room_indexes[room_id]):
        # Init
        for dev in room[room_id]:
            dev.rot = Vector3()
            dev.pos.x = 0
            dev.pos.z = 0
        # Calculate
        for idx, val in enumerate(room_indexes[room_id]):
            if idx < count - 1:
                DeviceArrangement.setUsingLine(room[room_id][val], room[room_id][room_indexes[room_id][idx+1]])
        for e in room[room_id]:
            ret.append(e.get2dPoints())
        print(ret)
        si.emit('draw', ret, room=room_id)
        # Reset
        room_indexes[room_id] = []
    elif count > len(room_indexes[room_id]):
        # Listening,,,
        return

    
    # DeviceArrangement.setUsingLine(room[room_id][0], room[room_id][1])


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