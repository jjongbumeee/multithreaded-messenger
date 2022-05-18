# admin.py
import protocol
from configparser import ConfigParser
from commonSocket import CommonSocket

config = ConfigParser()
config.read('config.ini')

HOST = config['DEFAULT']['HOST']
PORT = int(config['DEFAULT']['PORT'])


class AdminSocket(CommonSocket):
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

    def _killAllUser(self):
        killAllMsg = protocol.killAllUser()
        self.sendMsg(killAllMsg)

    def _printServerStat(self):
        print()
        reqServerStatMsg = protocol.reqServerStat()
        self.sendMsg(reqServerStatMsg)
        resMsg = self.recv()
        if resMsg['proto'] == 'RES_SERVER_STAT':
            print('CPU Utilization:', resMsg['cpu'], '%')
            print('Memory Available:', resMsg['mem']/1024/1024, 'MB')
            print('Number of client(s):', resMsg['clientNum'])
            print('Connections:', end=' ')
            if len(resMsg['connections']) == 0:
                print('None')
            else:
                print('')
            for name, friends in resMsg['connections'].items():
                print('\t', name, '=>', friends)
        else:
            raise ConnectionError('')

    def _printClientStat(self):
        print('Which client info do you want?')
        name = input()
        print()
        if name in self._listProc():
            reqClientStatMsg = protocol.reqClientStat(name)
            self.sendMsg(reqClientStatMsg)
            resMsg = self.recv()
            if resMsg['proto'] == 'RES_CLIENT_STAT':
                print(f'client [{name}]\nresource status')
                print('CPU Utilization:', resMsg['cpu'], '%')
                print('Memory Available:', resMsg['mem'] / 1024 / 1024, 'MB')
                print('Connections:', resMsg['connections'])
            else:
                raise ConnectionError('')
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
                self._killAllUser()
            elif menuSelect == 4:
                self._printServerStat()
            elif menuSelect == 5:
                self._printClientStat()
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
    admin = AdminSocket(HOST, PORT)
    admin.connect()
    admin.run()
