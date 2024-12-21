def werte(auswahl=''):
    angaben={'ssid':'wlanname'}
    angaben['password']='wlanpasswort'
    angaben['player']='squeezeclient'
    angaben['server']='http://lmsserverip:9000/jsonrpc.js'
    angaben['rfid']='http://rfidserverip:8001'
    if auswahl in list(angaben.keys()):
        return angaben[auswahl]
    else:
        return None
    
    