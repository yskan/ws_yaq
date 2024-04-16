import json
import datetime
from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
sock = Sock(app)
clients = []

count = 0

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/ws')
def echo(sock):
    clients.append(sock)
    while True:
        data = sock.receive()
        print(data)
        if data == "CLICK":
            global count
            count += 1
            response = { "count": count, "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            for s in clients:
                s.send(json.dumps(response))
        elif data == "close":
            clients.remove(sock)
            sock.close()
        else:
            err_response = { "error": "Invalid request", "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            sock.send(json.dumps(err_response))
        # print(data)
        # sock.send(data)

if __name__ == "__main__":
    app.run()