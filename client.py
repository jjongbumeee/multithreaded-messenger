# client.py
import socket
import threading
import protocol
import json
from datetime import datetime

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
        # TODO: json dump처리
        data = msg.encode()
        self.client_socket.send(data)

    def _recv(self):
        data = self.client_socket.recv(1024)
        msg = data.decode()
        return msg

    def close(self):
        return self.client_socket.close()

    def connect(self):
        # REQ_NAME recv
        reqName = json.loads(self._recv())
        print(reqName)
        try:
            if reqName['proto'] == 'REQ_NAME':

                # RES_NAME send
                self.myName = input()
                resNameMsg = protocol.resClientName(self.myName)
                self._sendMsg(json.dumps(resNameMsg))

                # SEND_FRI_LIST recv
                friendListMsg = json.loads(self._recv())
                if friendListMsg['proto'] == 'SEND_FRI_LIST':
                    self.friendList = friendListMsg['contents']
                    print(friendListMsg['contents'])

                    # ACK send
                    ackMsg = protocol.ack()
                    self._sendMsg(json.dumps(ackMsg))
                else:
                    raise ConnectionAbortedError('friend list exchange protocol error')
            else:
                raise ConnectionRefusedError('protocol sync error')
        except ConnectionError as error:
            print(error)

    def _msgHandler(self):
        try:
            while True:
                msg = json.loads(self._recv())
                if msg['proto'] == 'SEND_MSG':
                    print(f"""({datetime.now().strftime('%Y-%m-%d %H:%M')}) {msg['sender']} : {msg['message']}""")
        except Exception as e:
            print(e)

    def openRecvThread(self):
        self.recvHandler = threading.Thread(target=self._msgHandler)
        self.recvHandler.daemon = True
        self.recvHandler.start()

    def sendMsgToFriend(self, friend, msg):
        # friend validate
        if friend not in self.friendList:
            raise Exception(f"You don't have '{friend}' friend")
        sendMsgProto = protocol.sendMsg(msg, self.myName, 'uni', friend)
        self._sendMsg(json.dumps(sendMsgProto, default=str, indent=2))

    def sendBroadcast(self, msg):
        broadMsg = protocol.sendMsg(msg, self.myName, 'broad', 'all')
        self._sendMsg(json.dumps(broadMsg, default=str, indent=2))

    def sendMulticast(self, receivers, msg):
        for receiver in receivers:
            multiMsg = protocol.sendMsg(msg, self.myName, 'multi', receiver)
            self._sendMsg(json.dumps(multiMsg, default=str, indent=2))
        # self._sendMsg(f'm{self.myName}@{receivers}@{msg}')
        # print(self._recvMsg())


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