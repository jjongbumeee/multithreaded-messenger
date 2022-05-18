# commonSocket.py
import socket
import json
import os
import psutil
import signal
import time
import protocol


def signalHandler(signum, _):
    print()
    print(signal.Signals(signum).name, 'delivered')
    psutil.Process(os.getpid()).terminate()


class CommonSocket:
    def __init__(self, ipAddr, port):
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connInfo = (ipAddr, port)
        self.mySocket.connect(self.connInfo)
        self.connected = True
        self.myName = ''
        signal.signal(signal.SIGINT, signalHandler)

    def sendMsg(self, msg):
        msg = json.dumps(msg, default=str, indent=2)
        data = msg.encode()
        self.mySocket.send(data)

    def reconnect(self, maxRetry=5):
        self.connected = False
        print('reconnecting', end='', flush=True)
        for i in range(maxRetry):
            try:
                self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.mySocket.connect(self.connInfo)
                print('\nreconnected', flush=True)
                self.connected = True
                nameReqMsg = self.recv()
                if nameReqMsg['proto'] == 'REQ_NAME':
                    self.sendMsg(protocol.resClientName(self.myName))
                    self.recv()
                    self.sendMsg(protocol.ack())
                return
            except socket.error as e:
                time.sleep(5)
                print('.', end='', flush=True)
        print('reconnect failed')
        psutil.Process(os.getpid()).terminate()

    def recv(self):
        data = self.mySocket.recv(1024)
        if len(data) == 0:
            self.reconnect()
        msg = data.decode()
        return json.loads(msg)

    def close(self):
        return self.mySocket.close()
