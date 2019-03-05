from flask import Flask, request, render_template, jsonify, session, json, redirect, url_for


app = Flask(__name__)
app.secret_key = 'the random string'


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("roomDoor.html")

@app.route('/roomInit', methods=['POST'])
def roomInit():
    session['room_id'] = request.form['room_id']
    return redirect(url_for('room',id = session['room_id']))

@app.route('/room/<int:id>', methods=['POST', 'GET'])
def room(id):
    return render_template("canvas.html")


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0')
