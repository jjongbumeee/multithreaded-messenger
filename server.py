# server.py
import socket
import threading
import protocol
from queue import Queue
import json

MSGPREFIX = 'SERVER'


class ServerSocket:
    def __init__(self, port):
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketPool = {}
        self.initFriends = ['jay', 'hun']

    def _send(self, client, msg):
        msg = json.dumps(msg, default=str, indent=2)
        client.send(msg.encode())

    def _recv(self, client):
        data = client.recv(1024)
        if not data:
            raise Exception('connection closed')
        return data.decode()

    def _getInitFriendList(self, name):
        friendList = []
        for initFriend in self.initFriends:
            if initFriend != name:
                friendList.append(initFriend)
        return friendList

    def _connectionInit(self, clientSocketObj):
        # request client name (REQ_NAME) send
        msg = protocol.reqClientName()
        self._send(clientSocketObj, msg)

        # response client name (RES_NAME) recv
        try:
            nameRes = json.loads(self._recv(clientSocketObj))
            if nameRes['proto'] == 'RES_NAME' and nameRes['result'] == 200:
                name = nameRes['name']
                self.socketPool[name] = {
                    'socket': clientSocketObj,
                    'friends': [],
                }
                # friends list initialize
                self.socketPool[name]['friends'] = self._getInitFriendList(name)

                # send friend list (SEND_FRI_LIST) send
                friendsListMsg = protocol.sendFriendList(clientSocketObj, self.socketPool[name]['friends'])
                self._send(clientSocketObj, friendsListMsg)

                # ack wait (ACK) recv
                ackRes = json.loads(self._recv(clientSocketObj))
                if ackRes['proto'] == 'ACK' and ackRes['result'] == 200:
                    # for debug
                    # print(self.socketPool)
                    print(f'{name} client connected')
                else:
                    raise ConnectionError('ack error has occurred')
            else:
                raise ConnectionAbortedError('name response from client is abnormal')
        except ConnectionError as e:
            print(e)

    def _friendMsgHandle(self, client):
        msg = json.loads(self._recv(client))
        if msg['proto'] == 'SEND_MSG':
            if msg['method'] == 'broad':
                print(f'{msg["sender"]} > ALL : {msg["message"]}')
                for name, data in self.socketPool.items():
                    broadMsg = protocol.sendMsg(msg['message'], msg['sender'], 'broad', name)
                    self._send(data['socket'], broadMsg)

            elif msg['method'] == 'uni':
                print(f"{msg['sender']} > {msg['receiver']} : {msg['message']}")
                if msg['receiver'] not in self.socketPool[msg['sender']]['friends']:
                    raise AssertionError('friends are not connected')
                elif msg['receiver'] not in self.socketPool.keys():
                    errMsg = protocol.sendMsg(f"{client} is unconnected", "SERVER", 'uni', msg['sender'])
                    self._send(client, errMsg)
                else:
                    sendMsg = protocol.sendMsg(msg['message'], msg['sender'], 'uni', msg['receiver'])
                    print(sendMsg)
                    self._send(self.socketPool[msg['receiver']]['socket'], sendMsg)

            elif msg['method'] == 'multi':
                # TODO: uni로 변경하는 작업
                print(f"{msg['sender']} > {msg['receiver']} : {msg['message']}")
                if msg['receiver'] not in self.socketPool.keys():
                    errMsg = protocol.sendMsg(f"{client} is unconnected", "SERVER", 'uni', msg['sender'])
                    self._send(client, errMsg)
                else:
                    sendMsg = protocol.sendMsg(msg['message'], msg['sender'], 'multi', msg['receiver'])
                    print(sendMsg)
                    self._send(self.socketPool[msg['receiver']]['socket'], sendMsg)
                # sender, receivers, msg = msg.split('@')
                # mailList = map(str.strip, receivers[1:-1].replace("'", '').split(','))
                # print(sender, mailList, msg)
                # for receiver in mailList:
                #     self._send(self.socketMap[receiver], f'{sender}@{msg}')
                # self._send(client, f'{MSGPREFIX}@{sender} >> {receivers} : {msg}')
        else:
            raise ConnectionAbortedError('protocl error')

    def _handler(self, clientSocketObj, addr):
        print('Connected by', addr)
        try:
            self._connectionInit(clientSocketObj)
            while True:
                self._friendMsgHandle(clientSocketObj)
        except Exception as e:
            print(f'{addr} => except : {e}')

    def connect(self):
        self.serverSocket.bind(('', self.port))
        self.serverSocket.listen()
        try:
            while True:
                clientSocketObj, addr = self.serverSocket.accept()
                th = threading.Thread(target=self._handler, args=(clientSocketObj, addr))
                th.daemon = True
                th.start()
        except Exception as e:
            print(e)

    def close(self):
        return self.serverSocket.close()

    def reqClientName(self, clientSocket):

        self._send(clientSocket, )


if __name__ == '__main__':
    serverSocket = ServerSocket(20000)
    serverSocket.connect()