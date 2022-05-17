# client.py
import configparser
from commonSocket import commonSocket
import threading
import protocol
import json
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])


class ClientSocket(commonSocket):
    def __init__(self, ipAddr, port):
        super().__init__(ipAddr, port)
        self.friendList = []
        self.recvHandler = ''
        self.myName = ''

    def connect(self):
        # REQ_NAME recv
        reqName = json.loads(self.recv())
        print(reqName)
        try:
            if reqName['proto'] == 'REQ_NAME':

                # RES_NAME send
                self.myName = input()
                resNameMsg = protocol.resClientName(self.myName)
                self.sendMsg(resNameMsg)

                # SEND_FRI_LIST recv
                friendListMsg = json.loads(self.recv())
                if friendListMsg['proto'] == 'SEND_FRI_LIST':
                    self.friendList = friendListMsg['contents']
                    print(friendListMsg['contents'])

                    # ACK send
                    ackMsg = protocol.ack()
                    self.sendMsg(ackMsg)
                else:
                    raise ConnectionAbortedError('friend list exchange protocol error')
            else:
                raise ConnectionRefusedError('protocol sync error')
        except ConnectionError as error:
            print(error)

    def _msgHandler(self):
        try:
            # print received messages
            while True:
                msg = json.loads(self.recv())
                if msg['proto'] == 'SEND_MSG':
                    print(f"""({datetime.now().strftime('%Y-%m-%d %H:%M')}) {msg['sender']} : {msg['message']}""")
        except Exception as e:
            print(e)

    def openRecvThread(self):
        # receiving thread
        self.recvHandler = threading.Thread(target=self._msgHandler)
        self.recvHandler.daemon = True
        self.recvHandler.start()

    def sendMsgToFriend(self, friend, msg):
        # friend validate
        if friend not in self.friendList:
            raise Exception(f"You don't have '{friend}' friend")
        sendMsgProto = protocol.sendMsg(msg, self.myName, 'uni', friend)
        self.sendMsg(sendMsgProto)

    def sendBroadcast(self, msg):
        broadMsg = protocol.sendMsg(msg, self.myName, 'broad', 'all')
        self.sendMsg(broadMsg)

    def sendMulticast(self, recvs, msg):
        multiMsg = protocol.sendMsg(msg, self.myName, 'multi', recvs)
        self.sendMsg(multiMsg)


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
