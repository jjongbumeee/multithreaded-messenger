# admin.py
import protocol
import threading
from configparser import ConfigParser
from commonSocket import commonSocket

config = ConfigParser()
config.read('config.ini')

HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])


class adminSocket(commonSocket):
    def __init__(self, ipAddr, port):
        super().__init__(ipAddr, port)

    def _listProc(self):
        reqProcListMsg = protocol.reqListProc()
        self.sendMsg(reqProcListMsg)
        resProcListMsg = self.recv()
        return resProcListMsg['proc']

    def _killUser(self):
        print('Who do you want to kill?')
        target = input()
        if target in self._listProc():
            killUserMsg = protocol.killUser(target)
            self.sendMsg(killUserMsg)
        else:
            print("[ERROR] process doesn't exist. please check")

    def run(self):
        while True:
            print()
            print('1: list processes')
            print('2: kill process')
            print('3: kill all processes')
            print('4: view server resources')
            print('5: view client resources')
            menuSelect = int(input())
            if menuSelect == 1:
                print(self._listProc())
            elif menuSelect == 2:
                self._killUser()
            elif menuSelect == 3:
                pass
            elif menuSelect == 4:
                pass
            elif menuSelect == 5:
                pass
            else:
                pass

    def connect(self):
        reqClientName = self.recv()
        if reqClientName['proto'] == 'REQ_NAME':
            adminAuthMsg = protocol.isAdmin()
            self.sendMsg(adminAuthMsg)
        else:
            raise ConnectionError('protocol error')


if __name__ == '__main__':
    admin = adminSocket(HOST, PORT)
    admin.connect()
    admin.run()
