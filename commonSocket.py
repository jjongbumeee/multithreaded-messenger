# commonSocket.py
import socket
import json


class commonSocket:
    def __init__(self, ipAddr, port):
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mySocket.connect((ipAddr, port))

    def sendMsg(self, msg):
        msg = json.dumps(msg, default=str, indent=2)
        data = msg.encode()
        self.mySocket.send(data)

    def recv(self):
        data = self.mySocket.recv(1024)
        msg = data.decode()
        return json.loads(msg)

    def close(self):
        return self.mySocket.close()