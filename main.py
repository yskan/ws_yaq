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
        
        # Handle client disconnection
        if data == "close":
            clients.remove(sock)
            sock.close()
        
        # Parse incoming data
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            err_response = { "error": "Invalid request", "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            sock.send(json.dumps(err_response))
            continue
        
        event_type = data.get("event_type")
        print(event_type)
        # Handle incoming events
        if event_type == "click":
            global count
            count += 1
            response = { "count": count, "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            for s in clients:
                s.send(json.dumps(response))
        
        if event_type == "bullshit":
            err_response = { "error": "Bullshit ERROR", "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            sock.send(json.dumps(err_response))
        
if __name__ == "__main__":
    app.run()