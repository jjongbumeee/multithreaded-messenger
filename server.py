# server.py
import socket
import threading
import protocol

MSGPREFIX = 'SERVER'


class ServerSocket:
    def __init__(self, port):
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketMap = {}
        self.friendMap = {}

    def _send(self, client, msg):
        client.send(msg.encode())

    def _recv(self, client):
        data = client.recv(1024)
        if not data:
            raise Exception('connection closed')
        return data.decode()

    def _connectionInit(self, clientSocketObj):
        self._send(clientSocketObj, protocol.reqClientName())
        # self._send(clientSocketObj, f"{MSGPREFIX}@What's your name?")
        name = self._recv(clientSocketObj)
        self.socketMap[name] = clientSocketObj
        if name not in self.friendMap:
            self.friendMap[name] = ['jay', 'hun']
        self._send(clientSocketObj, f"[{' '.join(self.friendMap[name])}]")
        print(self.socketMap)
        print(self.friendMap)
        res = self._recv(clientSocketObj)
        if res != f'{MSGPREFIX}@success':
            raise Exception('Connection failed')

    def _friendMsgHandle(self, client):
        msg = self._recv(client)
        ubType = msg[:1]
        msg = msg[1:]
        if ubType == 'b':
            sender, msg = msg.split('@')
            print(sender, msg)
            for _, receiver in self.socketMap.items():
                self._send(receiver, f'{sender}@{msg}')
                self._send(client, f'{MSGPREFIX}@{sender} >> all : {msg}')
        elif ubType == 'u':
            sender, receiver, msg = msg.split('@')
            print(sender, receiver, msg)
            if receiver not in self.friendMap[sender]:
                raise Exception('Friends are not connected')
            elif receiver not in self.socketMap:
                self._send(client, f'{MSGPREFIX}@Receiver is not connected')
            else:
                self._send(self.socketMap[receiver], f'{sender}@{msg}')
                self._send(client, f'{MSGPREFIX}@{sender} >> {receiver} : {msg}')
        elif ubType == 'm':
            sender, receivers, msg = msg.split('@')
            mailList = map(str.strip, receivers[1:-1].replace("'", '').split(','))
            print(sender, mailList, msg)
            for receiver in mailList:
                self._send(self.socketMap[receiver], f'{sender}@{msg}')
            self._send(client, f'{MSGPREFIX}@{sender} >> {receivers} : {msg}')

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