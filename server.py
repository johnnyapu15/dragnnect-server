from flask import Flask, request, \
render_template, jsonify, session, \
json, redirect, url_for

import flask_socketio as si


app = Flask(__name__)
app.secret_key = 'the random string'
socketio = si.SocketIO(app, manage_session=False)


# GLOBAL VAR
room_count = dict()
room = dict() # email -> room id

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
    print("Joining into " + id_str + "...")
    #print("Index: " + len(room[id_str]))
    return render_template("canvas.html", count = room_count[id_str], room_id = id_str)

@app.route('/room/<int:id>', methods=['POST', 'GET'])
def room_func(id):
    id_str = str(id)
    return render_template("canvas.html", count = str(len(room[id_str])), room_id = id_str)

@socketio.on('join')
def join_room(data):
    print(data)
    id = data['data']['id']
    id_str = str(id)
    if not(id_str in room.keys()):
        room[id_str] = []
    room[id_str].append(request.sid)
    si.join_room(id_str)
    print("------------------------Log-----------------------")
    print(si.rooms())
    print("Joining into " + id_str + "...")
    print("SID: " + str(request.sid))
    print("Index: " + str(room_count[id_str]))
    si.emit('update', {'count':room_count[id_str]}, room = id_str)
    #si.emit('redirect', {'url':url_for('room_func', id = id_str)})

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
# @socketio.on('disconnect')

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
# @socketio.on('leave')
@app.route('/quit', methods=['POST', 'GET'])
def quit_callback():
    #id = str(data['data']['id'])
    print("quit")
    print(session)
    id = session['room_id']
    print(id)
    #sid = str(request.json['sid'])
    #room[id].remove(sid)
    #si.leave_room(id)
    si.emit('update', {'count':room_count[id]}, room = id)
    print("Quiting..." + id)
    return str(request.json)

@app.route('/room/callback', methods=['POST', 'GET'])
def callback():
    print(request.json)
    return str(request.json)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    #app.run(host='0.0.0.0')
    socketio.run(app, host='0.0.0.0')
