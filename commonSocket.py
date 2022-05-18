# commonSocket.py
import socket
import json
import os
import psutil
import signal


def signalHandler(signum, _):
    print()
    print(signal.Signals(signum).name, 'delivered')
    psutil.Process(os.getpid()).terminate()


class CommonSocket:
    def __init__(self, ipAddr, port):
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mySocket.connect((ipAddr, port))
        self.myName = ''
        signal.signal(signal.SIGINT, signalHandler)

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
