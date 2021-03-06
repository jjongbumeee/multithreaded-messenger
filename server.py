# server.py
import configparser
import socket
import threading
import psutil
import protocol
import json
from pprint import pprint

config = configparser.ConfigParser()
config.read('config.ini')


class ServerSocket:
    def __init__(self, port):
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketPool = {}
        self.initFriends = [s.strip() for s in config['DEFAULT']['INIT_FRI'].split(',')]
        self.adminSocket = {}
        print(self.initFriends)

    def _send(self, client, msg):
        msg = json.dumps(msg, default=str, indent=2)
        client.send(msg.encode())

    def _recv(self, client):
        data = client.recv(1024)
        if not data:
            raise Exception('connection closed')
        return json.loads(data.decode())

    def _getInitFriendList(self, name):
        friendList = []
        for initFriend in self.initFriends:
            if initFriend != name:
                friendList.append(initFriend)
        return friendList

    def _clientConnectionInit(self, clientSocketObj):
        # request client name (REQ_NAME) send
        msg = protocol.reqClientName()
        self._send(clientSocketObj, msg)

        # response client name (RES_NAME) recv
        try:
            nameRes = self._recv(clientSocketObj)
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
                ackRes = self._recv(clientSocketObj)
                if ackRes['proto'] == 'ACK' and ackRes['result'] == 200:
                    # for debug
                    # print(self.socketPool)
                    print(f'{name} client connected')
                else:
                    raise ConnectionError('ack error has occurred')
                return True
            elif nameRes['proto'] == 'CONF_ADMIN':
                return False
            else:
                raise ConnectionAbortedError('name response from client is abnormal')
        except ConnectionError as e:
            print(e)

    def _friendMsgHandle(self, client):
        msg = self._recv(client)
        # validate proto
        if msg['proto'] == 'SEND_MSG':
            # broadcast
            if msg['method'] == 'broad':
                print(f'{msg["sender"]} > ALL : {msg["message"]}')
                for name, data in self.socketPool.items():
                    broadMsg = protocol.sendMsg(msg['message'], msg['sender'], 'broad', name)
                    self._send(data['socket'], broadMsg)

            # unicast
            elif msg['method'] == 'uni':
                print(f"{msg['sender']} > {msg['receiver']} : {msg['message']}")
                # each other are not friends
                if msg['receiver'] not in self.socketPool[msg['sender']]['friends']:
                    raise AssertionError('friends are not connected')
                # receiver client is unconnected
                elif msg['receiver'] not in self.socketPool.keys():
                    errMsg = protocol.sendMsg(f"{client} is unconnected", "SERVER", 'uni', msg['sender'])
                    self._send(client, errMsg)
                # send message
                else:
                    sendMsg = protocol.sendMsg(msg['message'], msg['sender'], 'uni', msg['receiver'])
                    print(sendMsg)
                    self._send(self.socketPool[msg['receiver']]['socket'], sendMsg)

            # multicast
            elif msg['method'] == 'multi':
                print(f"{msg['sender']} > {msg['receiver']} : {msg['message']}")
                # receiver client is unconnected
                for target in msg['receiver']:
                    if target not in self.socketPool.keys():
                        errMsg = protocol.sendMsg(f"{client} is unconnected", "SERVER", 'uni', msg['sender'])
                        self._send(client, errMsg)
                    # send message
                    else:
                        sendMsg = protocol.sendMsg(msg['message'], msg['sender'], 'multi', target)
                        print(sendMsg)
                        self._send(self.socketPool[target]['socket'], sendMsg)
        elif msg['proto'] == 'RES_CLIENT_STAT':
            serverResMsg = protocol.resClientStat(msg['cpu'], msg['mem'], msg['name'],
                                                  self.socketPool[msg['name']]['friends'])
            self._send(self.adminSocket, serverResMsg)
        else:
            raise ConnectionAbortedError('protocol error')

    # 1. list processes
    def _listProc(self, adminSoc):
        procListMsg = protocol.resListProc(list(self.socketPool.keys()))
        self._send(adminSoc, procListMsg)

    # 2. kill process
    def _killProc(self, name, adminSoc):
        if name in list(self.socketPool.keys()):
            killUserMsg = protocol.killUser(name)
            self._send(self.socketPool[name]['socket'], killUserMsg)
            del self.socketPool[name]
        else:
            errorMsg = protocol.ack(result=404)
            errorMsg['msg'] = 'user not found'
            self._send(adminSoc, errorMsg)

    # 3. kill all processes
    def _killAllProc(self):
        for sockName, sockItem in self.socketPool.items():
            killUserMsg = protocol.killUser(sockName)
            self._send(sockItem['socket'], killUserMsg)
        self.socketPool.clear()

    # delete socket by 'sock'
    def _delSocket(self, sock):
        for name, val in self.socketPool.items():
            if val['socket'] == sock:
                del self.socketPool[name]
                return

    # 4. view server resources
    def _monitorServerStat(self, adminSocket):
        friendConnections = {}
        for name, val in self.socketPool.items():
            friendConnections[name] = val['friends']
        monitoringMsg = protocol.resServerStat(psutil.cpu_percent(), psutil.virtual_memory().available,
                                               len(self.socketPool), friendConnections)
        pprint(monitoringMsg)
        self._send(adminSocket, monitoringMsg)

    # view client resources
    def _monitorClientStat(self, adminSocket, clientName):
        self.adminSocket = adminSocket
        clientReqMsg = protocol.reqClientStat(clientName)
        if clientName in list(self.socketPool.keys()):
            self._send(self.socketPool[clientName]['socket'], clientReqMsg)
            clientResMsg = self._recv(self.socketPool[clientName]['socket'])
            if clientResMsg['proto'] == 'RES_CLIENT_STAT':
                serverResMsg = protocol.resClientStat(clientResMsg['cpu'], clientResMsg['mem'],
                                                      self.socketPool[clientName]['friends'])
                self._send(adminSocket, serverResMsg)
            else:
                raise ConnectionError('protocol error')
        else:
            print('ERROR')
            raise Exception('client name not found')

    def _adminMsgHandle(self, adminSocket):
        msg = self._recv(adminSocket)
        if msg['proto'] == 'REQ_LIST_PROC':
            self._listProc(adminSocket)
        elif msg['proto'] == 'KILL_USER':
            self._killProc(msg['name'], adminSocket)
        elif msg['proto'] == 'KILL_ALL':
            self._killAllProc()
        elif msg['proto'] == 'REQ_SERVER_STAT':
            self._monitorServerStat(adminSocket)
        elif msg['proto'] == 'REQ_CLIENT_STAT':
            self._monitorClientStat(adminSocket, msg['name'])

    def _handler(self, clientSocketObj, addr):
        print('Connected by', addr)
        try:
            # client connection initialize (Admin client returns FALSE)
            if self._clientConnectionInit(clientSocketObj):
                while True:
                    # message handling
                    self._friendMsgHandle(clientSocketObj)
            else:
                while True:
                    self._adminMsgHandle(clientSocketObj)

        except Exception as e:
            self._delSocket(clientSocketObj)
            print(f'{addr} => {e}')
            # pprint(self.socketPool)

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


if __name__ == '__main__':
    serverSocket = ServerSocket(20000)
    serverSocket.connect()
