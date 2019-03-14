from flask import Flask, request, \
render_template, jsonify, session, \
json, redirect, url_for

import flask_socketio as si


app = Flask(__name__)
app.secret_key = 'the random string'
socketio = si.SocketIO(app)


# GLOBAL VAR
room_count = dict()

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("roomDoor.html")

@app.route('/roomInit', methods=['POST'])
def roomInit():
    return redirect(url_for('room',id = request.form['room_id']))

@app.route('/room/<int:id>', methods=['POST', 'GET'])
def room(id):
    id_str = str(id)
    print(room_count.keys())
    print(id_str)
    if not(id_str in room_count.keys()):
        room_count[id_str] = 0
    room_count[id_str] += 1
    print(room_count[id_str])
    return render_template("canvas.html", count = room_count[id_str], room_id = id_str)

@app.route('/room/quit', methods=['POST', 'GET'])
def quit_callback():
    id = str(request.json['id'])
    room_count[id] -= 1
    print(room_count[id])
    return str(request.json)

@app.route('/room/callback', methods=['POST', 'GET'])
def callback():
    print(request.json)
    return str(request.json)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0')
