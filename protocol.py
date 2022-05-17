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
        'result': result
    }


def isAdmin(password='1234'):
    return {
        'proto': 'CONF_ADMIN',
        'receiver': 'SERVER',
        'password': password
    }


def listProcesses():
    return {
        'proto': 'LIST_PROC'
    }


def killUser(pid):
    return {
        'proto': 'KILL_USER',
        'pid': pid
    }


def killAllUser():
    return {
        'proto': 'KILL_ALL'
    }


def monitorServerResource(menu):
    return {
        'proto': 'SERVER_RESOURCE'
    }