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


def isAdmin():
    return {
        'proto': 'CONF_ADMIN',
        'receiver': 'SERVER',
        'password': '1234'
    }
