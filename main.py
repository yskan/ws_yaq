import json
import datetime
from flask import Flask, render_template
from flask_sock import Sock

app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
sock = Sock(app)
clients = []
clients_map = {}
reversed_clients_map = {}

count = 0

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/ws')
def echo(sock):
    while True:
        data = sock.receive()
        print("Data RECV: ", data)

        # Handle client disconnection
        if data == "close":
            clients.remove(sock)
            username = reversed_clients_map[sock]
            print("User disconnected: ", username)
            del reversed_clients_map[sock]
            del clients_map[username]
            sock.close()
        
        # Parse incoming data
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            err_response = { "error": "Invalid request", "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            sock.send(json.dumps(err_response))
            continue
        
        event_type = data.get("event_type")
        print("Event_type: ", event_type)

        # Handle incoming events
        if event_type == "delete_me":
            username = reversed_clients_map[sock]
            print("User disconnected: ", username)
            del reversed_clients_map[sock]
            del clients_map[username]
            sock.close()

        if event_type == "register_username":
            username = data.get("username")
            clients_map[username] = sock
            reversed_clients_map[sock] = username
            print(clients_map)
            for u, s in clients_map.items():
                print("Sending new client event to: ", u)
                s.send(json.dumps({ "event_type": "new_client", "username": username}))

        if event_type == "click":
            global count
            count += 1
            sender_username = reversed_clients_map[sock]
            response = { "username": sender_username, "count": count, "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            for s in clients_map.values():
                s.send(json.dumps(response))
        
        if event_type == "bullshit":
            err_response = { "error": "Bullshit ERROR", "tz": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }
            sock.send(json.dumps(err_response))
        
if __name__ == "__main__":
    app.run()