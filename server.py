from flask import Flask, request, render_template, jsonify, session, json


app = Flask(__name__)
app.secret_key = 'the random string'


@app.route('/', methods=['GET', 'POST'])
def index():
    return "Yes! or yes."

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0')
