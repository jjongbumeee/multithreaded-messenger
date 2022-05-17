# admin.py
import protocol
from configparser import ConfigParser
from commonSocket import commonSocket

config = ConfigParser()
config.read('config.ini')

HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])

class adminSocket(commonSocket):
    def __init__(self, ipAddr, port):
        super().__init__(ipAddr, port)

    def connect(self):
        reqClientName = self.recv()
        if reqClientName['proto'] == 'REQ_NAME':
            adminAuthMsg = protocol.isAdmin()
            self.sendMsg(adminAuthMsg)
        else:
            while True:
                print('1: list processes')
                print('2: kill process')
                print('3: kill all processes')
                print('4: view server resources')
                print('5: ')

if __name__ == '__main__':
    admin = adminSocket(HOST, PORT)
    admin.connect()