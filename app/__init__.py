from flask import Flask, jsonify, redirect, request
from flask_restful import reqparse
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests, json

class Server:
    def __init__(self, serverAddress, serverPort, serverName, currentPlayers, serverVersion, maxPlayers, mapName, is_official=False):
        self.serverName = serverName
        self.serverPort = serverPort
        self.currentPlayers = currentPlayers
        self.serverVersion = serverVersion
        self.maxPlayers = maxPlayers
        self.mapName = mapName
        self.serverAddress = serverAddress
        self.is_official = is_official
        self.lastUpdated = datetime.now().strftime("%Y-%m-%dT%XZ")


class Servers:
    def __init__(self):
        self.servers = []
        self.server_ips = []
    
    def add_server(self, server):
        if server.serverAddress in self.server_ips:
            new_servers = []
            for x in self.servers:
                if x.serverAddress == server.serverAddress:
                    pass
                else:
                    new_servers.append(x)
            self.servers = new_servers
            self.servers.append(server)
        else:
            self.servers.append(server)
            self.server_ips.append(server.serverAddress)


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
    servers.add_server(server)
    return "", 200

@app.route('/getservers', methods=['GET'])
def getservers():
    for s in servers.servers:
        print(s.serverAddress)
    parser = s_parser()
    args = parser.parse_args()
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
            servers.server_ips.remove(s.serverAddress)

sched = BackgroundScheduler()

trigger = IntervalTrigger(seconds=20)
sched.add_job(check_for_dead_servers, trigger)
sched.start()