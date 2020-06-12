from flask import Flask, jsonify, redirect, request
from flask_restful import reqparse
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class Server:
    def __init__(self, serverAddress, serverPort, serverName, currentPlayers, serverVersion, maxPlayers, mapName):
        self.serverName = serverName
        self.serverPort = serverPort
        self.currentPlayers = currentPlayers
        self.serverVersion = serverVersion
        self.maxPlayers = maxPlayers
        self.mapName = mapName
        self.serverAddress = serverAddress
        self.lastUpdated = datetime.now().strftime("%Y-%m-%dT%XZ")
    
    def update_server(self, server):
        self.serverName = server.serverName
        self.serverPort = server.serverPort
        self.currentPlayers = server.currentPlayers
        self.serverVersion = server.serverVersion
        self.maxPlayers = server.maxPlayers
        self.mapName = server.mapName
        self.lastUpdated = datetime.now().strftime("%Y-%m-%dT%XZ")

class Servers:
    def __init__(self):
        self.servers = []
    
    def add_server(self, server):
        if len(self.servers) > 0:
            for s in self.servers:
                if s.serverAddress == server.serverAddress:
                    s.update_server(server)
                else:
                    self.servers.append(server)
        else:
            self.servers.append(server)


app = Flask(__name__)

def ka_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('maxPlayers')
    parser.add_argument('serverName')
    parser.add_argument('currentPlayers')
    parser.add_argument('serverPort')
    parser.add_argument('serverVersion')
    parser.add_argument('mapName')
    return parser

servers = Servers()

@app.route('/')
def index():
    return redirect('https://sxlservers.com'), 200

@app.route('/serverinfo', methods=['POST'])
def serverinfo():
    parser = ka_parser()
    args = parser.parse_args()
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    server = Server(ip, **args)
    print(server.serverAddress)
    servers.add_server(server)
    print(servers.servers)
    return "", 200

@app.route('/getservers', methods=['GET'])
def getservers():
    obj = []
    for s in servers.servers:
        sobj = {
            "model": "api.server",
            "pk": 1503,
            "fields": {
                "name": s.serverName,
                "IP": s.serverAddress,
                "port": s.serverPort,
                "version": s.serverVersion,
                "mapName": s.mapName,
                "maxPlayers": s.maxPlayers,
                "currentPlayers": s.currentPlayers,
                "lastUpdated": s.lastUpdated
            }
        }
        obj.append(sobj)
    return jsonify(obj), 200


def check_for_dead_servers():
    for s in servers.servers:
        if datetime.strptime(s.lastUpdated, "%Y-%m-%dT%XZ") < datetime.now() - timedelta(seconds=30):
            servers.servers.remove(s)

sched = BackgroundScheduler()

trigger = IntervalTrigger(seconds=20)
sched.add_job(check_for_dead_servers, trigger)
sched.start()