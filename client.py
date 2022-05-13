# client.py
import socket
import threading
import re

HOST = '127.0.0.1'
PORT = 20000


class ClientSocket:
    def __init__(self, ipAddr, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ipAddr, port))
        self.friendList = []
        self.recvHandler = ''
        self._serverPrefix = ''
        self.myName = ''

    def _sendMsg(self, msg):
        data = msg.encode()
        self.client_socket.send(data)

    def _recv(self):
        data = self.client_socket.recv(1024)
        msg = data.decode()
        return msg

    def _recvMsg(self):
        msg = self._recv().split('@')
        print(msg)
        if self._serverPrefix == '':
            self._serverPrefix = msg[0]
        msgString = f'[{msg[0]}] {msg[1]}'
        return msgString

    def close(self):
        return self.client_socket.close()

    def connect(self):
        print(self._recvMsg())
        self.myName = input()
        self._sendMsg(self.myName)
        recvList = self._recv()
        try:
            self.friendList = re.sub('[\[\]]', '', recvList).split(' ')
            print(self.friendList)
        except Exception as exception:
            self._sendMsg(f'{self._serverPrefix}@fail')
            print(f'{exception}')
            return
        self._sendMsg(f'{self._serverPrefix}@success')

    def _msgHandler(self):
        while True:
            print(self._recvMsg())

    def openRecvThread(self):
        self.recvHandler = threading.Thread(target=self._msgHandler)
        self.recvHandler.start()

    def sendMsgToFriend(self, friend, msg):
        # friend validate
        if friend not in self.friendList:
            raise Exception(f"You don't have '{friend}' friend")
        self._sendMsg(f'u{self.myName}@{friend}@{msg}')
        # result
        print(self._recvMsg())

    def sendBroadcast(self, msg):
        self._sendMsg(f'b{self.myName}@{msg}')
        print(self._recvMsg())

    def sendMulticast(self, receivers, msg):
        self._sendMsg(f'm{self.myName}@{receivers}@{msg}')
        print(self._recvMsg())


if __name__ == '__main__':
    clientSocket = ClientSocket(HOST, PORT)
    clientSocket.connect()
    clientSocket.openRecvThread()
    try:
        while True:
            print('Select Unicast(u) / Broadcast(b) / Multicast(m)')
            type = input()
            if type == 'u':
                print('Who do you want to send message?')
                receiver = input()
                print('Insert your message')
                msg = input()
                clientSocket.sendMsgToFriend(receiver, msg)
            elif type == 'b':
                print('Insert your message')
                msg = input()
                clientSocket.sendBroadcast(msg)
            elif type == 'm':
                print('Who do you want to send message?')
                receivers = input().split(' ')
                print(receivers)
                print('Insert your message')
                msg = input()
                clientSocket.sendMulticast(receivers, msg)
            else:
                print('check your input value')
    except Exception as e:
        print(e)
        clientSocket.close()