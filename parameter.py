def werte(auswahl=''):
    angaben={'ssid':'wlanname'}
    angaben['password']='wlanpasswort'
    angaben['player']='squeezeclient'
    angaben['server']='http://lmsserverIp:9000/jsonrpc.js'
    angaben['rfid']='http://rfidserverIp:8001'
    angaben['sonoff']='http://sonoffIp'
    if auswahl in list(angaben.keys()):
        return angaben[auswahl]
    else:
        return None
    
    