def sendMsg(msg, sender, transMethod, receiver):
    return {
        'proto': 'SEND_MSG',
        'method': transMethod,
        'sender': sender,
        'receiver': receiver,
        'message': msg
    }


def reqClientName():
    return {
        'proto': 'REQ_NAME',
        'sender': 'SERVER'
    }


def resClientName(name='', result=200):
    return {
        'proto': 'RES_NAME',
        'receiver': 'SERVER',
        'result': result,
        'name': name
    }


def sendFriendList(receiver, friendMap):
    return {
        'proto': 'SEND_FRI_LIST',
        'receiver': receiver,
        'contents': friendMap
    }


def ack(result=200):
    return {
        'proto': 'ACK',
        'receiver': 'SERVER',
        'result': result,
        'msg': ''
    }


def isAdmin(password='1234'):
    return {
        'proto': 'CONF_ADMIN',
        'receiver': 'SERVER',
        'password': password
    }


def reqListProc():
    return {
        'proto': 'REQ_LIST_PROC'
    }


def resListProc(procList):
    return {
        'proto': 'RES_LIST_PROC',
        'proc': procList
    }


def killUser(name):
    return {
        'proto': 'KILL_USER',
        'name': name
    }


def resKillUser(name, result=200):
    return {
        'proto': 'RES_KILL_USER',
        'name': name,
        'result': result
    }


def killAllUser():
    return {
        'proto': 'KILL_ALL'
    }


def reqServerStat():
    return {
        'proto': 'REQ_SERVER_STAT',
    }


def resServerStat(utilization, memoryUsage, clientNum, connections):
    return {
        'proto': 'RES_SERVER_STAT',
        'cpu': utilization,
        'mem': memoryUsage,
        'clientNum': clientNum,
        'connections': connections
    }


def reqClientStat(name):
    return {
        'proto': 'REQ_CLIENT_STAT',
        'name': name
    }


def resClientStat(util, mem, name, conn=''):
    return {
        'proto': 'RES_CLIENT_STAT',
        'name': name,
        'cpu': util,
        'mem': mem,
        'connections': conn
    }
