"""
hello.py

    Writes "Hello!" in random colors at random locations on the display.
"""
import urequests
import ujson
from switch import Switch

import wlan
import parameter
import machine
import utime
import random
import time
import uping
import uasyncio as asyncio
import vga2_bold_16x32 as big
#import romans as big
import vga2_bold_16x16 as medium
#import italiccs as medium
import vga2_8x8 as small
#import romanp as small
import tft_config
import tft_buttons
import s3lcd

from machine import Pin, SPI
from mfrc522 import MFRC522

wlan.wlan_connect(ssid=parameter.werte('ssid'),password=parameter.werte('password'))

sck = Pin(3, Pin.OUT)
mosi = Pin(2, Pin.OUT)
miso = Pin(1, Pin.OUT)
spi = SPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

sda = Pin(10, Pin.OUT)

statusFailed=False
tft = tft_config.config(tft_config.WIDE)
tft.init()
BACKGROUND=s3lcd.BLACK
GREEN=s3lcd.GREEN
RED=s3lcd.RED
BLUE=s3lcd.BLUE

incSwitch = Switch(18)
decSwitch = Switch(44)
befSwitch = Switch(17)
nexSwitch = Switch(21)
selSwitch = Switch(43)


def decSwitch_changed(change):
    if change == decSwitch.SW_RELEASE:
        display.decIncKnopf(-1)
def incSwitch_changed(change):
    if change == incSwitch.SW_RELEASE:
        display.decIncKnopf(1)
def befSwitch_changed(change):
    if change == befSwitch.SW_RELEASE:
        display.befNexKnopf(-1)
def nexSwitch_changed(change):
    if change == nexSwitch.SW_RELEASE:
        display.befNexKnopf(1)
def selSwitch_changed(change):
    global zeitVor
    global display
    if change == selSwitch.SW_RELEASE:
        zeitNach=utime.ticks_ms()
        if zeitNach-zeitVor > 500:
            display.selGedrueckt('lang')
        elif zeitNach-zeitVor > 50:
            display.selGedrueckt('kurz')
    else:
        zeitVor= utime.ticks_ms()

incSwitch.add_handler(incSwitch_changed)
decSwitch.add_handler(decSwitch_changed)
befSwitch.add_handler(befSwitch_changed)
nexSwitch.add_handler(nexSwitch_changed)
selSwitch.add_handler(selSwitch_changed)


zeitVor=0


class displayInhalt:
    hauptmenu={'Volumen':'self.volumenDisplay()','Wiedergabeliste':'self.stelleMenuDar(self.wiedergabe,2)','Playerauswahl':'self.stelleMenuDar(self.playersMenue,2)','Zurueck':'self.ebeneNull()'}
    wiedergabe={'Sport':'self.playVari(["playlist","play","/home/share/PlayLists/Sport.m3u"]); self.ebeneNull();','Zufall':'self.playVari(["randomplay","tracks"]); self.ebeneNull();','FFN':'self.playUrl("http://player.ffn.de/ffnstream.mp3"); self.ebeneNull()','Zurueck':'self.stelleMenuDar(self.hauptmenu,1)'}
    playersMenue={}
    menuEbene=0
    index=0
    naechstesLied=''
    vorherigesLied=''
    textUntenEbeneNull='Druecke lang fuers Menue'
    textUntenMenue='Druecke lang fuer zurueck'
    aktuellesMenu=None
    aktIndex=0
    anzLieder=0
    sonoff=f'{parameter.werte("player")}{parameter.werte("sonoff")}'
    playercount=0
    untenRechts="RFID Frei"
    obenLinks=""
    def __init__(self, player=parameter.werte('player'),url=parameter.werte('server')):
        self.url=url
        self.player=player
        self.playerStart=player
        self.getPlayers()
        self.updatePlayer()
        self.ebeneNull()
    def updatePlayer(self,):
        self.getPlayers()
        if self.player:
            statjson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["status","-",1,"tags:al"]]})
            res=self.requestsAbfrage(data=statjson,ort='updatePlayer')
            if res==-1:
                global statusFailed
                statusFailed=True
                return
            jsondata=ujson.loads(res.text)
            self.lied=jsondata['result']['playlist_loop'][0]['title'] if 'playlist_loop' in jsondata['result'].keys() else ''
            self.volumen=jsondata['result']['mixer volume']
            self.playStatus=jsondata['result']['mode']
            self.status=self.playStatus
            self.getAktuelleLieder()
        else:
            self.lied=''
            self.volumen=0
            self.playStatus='Nichts'
            self.player=self.playerStart
            self.getPlayers()
#        print(jsondata['result'])
    def getPlayers(self,):
#        try:
        serverstatus=ujson.dumps({"id":1,"method":"slim.request","params":["",["serverstatus", 0, 999]]})
        res=self.requestsAbfrage(data=serverstatus,ort='getPlayers')
        if res==-1:
            self.player = None
            return
        jsondata=ujson.loads(res.text)
        self.playercount=jsondata['result']['player count']
        self.players={}
        self.playersMenue={}
        if self.playercount>0:
            for i in range(self.playercount):
                playername=jsondata['result']['players_loop'][i]['name']
                self.players[playername]=jsondata['result']['players_loop'][i]['playerid']
                self.playersMenue[playername]=f'self.player="{playername}"; self.ebeneNull()'
        self.player = self.player if self.player in self.players.keys() else None
#        except:
#            print('Probleme Player zu finden')
    def getAktuelleLieder(self,):
        self.lied='Nichts'
        self.vorherigesLied=''
        self.naechstesLied=''
#1 Frag den aktuellen Index ab
        jdata=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","index","?"]]})
        res=self.requestsAbfrage(data=jdata,ort='getAktuelleLieder')
        if res==-1:
            time.sleep_ms(500)
            res=self.requestsAbfrage(data=jdata,ort='getAktuelleLieder')
            if res==-1:
                return
        self.aktIndex=int(ujson.loads(res.text)['result']['_index'])
#2 Frag die Anzahl der Lieder ab.
        jdata=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","tracks","?"]]})
        res=self.requestsAbfrage(data=jdata,ort='getAktuelleLieder')
        if res==-1:
            return
        self.anzLieder=int(ujson.loads(res.text)['result']['_tracks'])
        jdata=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","title",f"{self.aktIndex}","?"]]})
        res=self.requestsAbfrage(data=jdata,ort='getAktuelleLieder')
        if res==-1:
            return
        self.lied=ujson.loads(res.text)['result']['_title']  #[0:20]
        if self.aktIndex>0:
            try:
                res=urequests.post(self.url, data = ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","title",f"{self.aktIndex-1}","?"]]}))
                self.vorherigesLied=ujson.loads(res.text)['result']['_title'][0:40]
            except:
                print('urequests Fehler in getAktuelleLieder vorheriges Lied')
        if self.aktIndex<self.anzLieder:
            try:
                res=urequests.post(self.url, data = ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","title",f"{self.aktIndex+1}","?"]]}))
                if '_title' in ujson.loads(res.text)['result']:
                    self.naechstesLied=ujson.loads(res.text)['result']['_title'][0:40]
            except:
                print('urequests Fehler in getAktuelleLieder naechstes Lied')
#        except:
#            self.lied='Leere Liste'
    def befNexKnopf(self,i):
        if self.menuEbene==2:
            self.stelleMenuDar(self.hauptmenu,1)
        elif self.menuEbene==1:
            self.ebeneNull()
        else:
            self.getAktuelleLieder()
            jdata=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","index",f"{self.aktIndex+i}"]]})
            res=self.requestsAbfrage(data=jdata,ort='Next Before -> Menu Ebene 0')
            if not res==-1:
                time.sleep_ms(100)
                self.updatePlayer()
                self.ebeneNull()
    def decIncKnopf(self,i):
        if self.menuEbene>0:
            if self.aktuellesMenu=='volumen':
                voljson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["mixer","volume",f"{'+' if i>0 else '-'}10"]]})
                res=self.requestsAbfrage(data=voljson,ort='decIncKnopf Volumen')
            else:
                self.index=(self.index+i) % len(self.hauptmenu) 
                self.stelleMenuDar(self.aktuellesMenu,self.menuEbene)
        else:
            voljson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["mixer","volume",f"{'+' if i>0 else '-'}10"]]})
            res=self.requestsAbfrage(data=voljson,ort='decIncKnopf Volumen')
            self.volumenDisplay()
    def stelleMenuDar(self,menu,ebene):
        self.aktuellesMenu=menu
        self.menuNamen=list(menu.keys())
        self.menuEbene=ebene
        lenMenu=len(self.menuNamen) 
        self.vorher=self.menuNamen[(self.index-1) % lenMenu]
        self.mitte=self.menuNamen[self.index % lenMenu]
        self.naechste=self.menuNamen[(self.index+1) % lenMenu]
        self.unten=self.textUntenMenue
        self.status=''    
        self.updateDisplay()
    def ebeneNull(self,):
        self.menuEbene=0
        self.vorher=self.vorherigesLied
        self.mitte=self.lied
        self.naechste=self.naechstesLied
        self.status=self.playStatus
        self.unten=self.textUntenEbeneNull
        self.updateDisplay()
    def selGedrueckt(self,pushLaenge):
        if self.menuEbene==0:
            if pushLaenge=='kurz':
                if self.playStatus=='play':
                    statjson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["pause"]]})
                else:
                    statjson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["play"]]})
                res=self.requestsAbfrage(data=statjson,ort='knopfGedrueckt')
                self.updatePlayer()
                self.updateDisplay()
            if pushLaenge=='lang':
                self.stelleMenuDar(self.hauptmenu,1)
        else:
            if self.aktuellesMenu=='volumen':
                self.ebeneNull()
            else:
                if pushLaenge=='kurz':
                    exec(self.aktuellesMenu[self.mitte], {"self": self})
                else:
                    self.ebeneNull()     
    def updateDisplay(self,):
        tft.fill(BACKGROUND)
        if len(self.sonoff)>0:
            if self.frageSonoffAb():
                tft.text(small,self.obenLinks,0,0,GREEN)
        if self.player:
            tft.text(big,self.player if self.player else 'Keiner' ,tft.width()-(len(self.player) if self.player else len('Keiner')) * big.WIDTH,0,GREEN)
        tft.text(small,self.vorher,0,tft.height() // 2 - big.HEIGHT // 2-small.HEIGHT,GREEN)
        n=len(self.mitte)
        if n>25:        
            tft.text(medium,self.mitte[0:20],0,tft.height() // 2 - medium.HEIGHT // 2,BLUE)       
            tft.text(medium,self.mitte[20:min(40,n)],0,tft.height() // 2 + medium.HEIGHT // 2,BLUE)
        else:        
            tft.text(big,self.mitte[0:min(20,n)],0,tft.height() // 2 - big.HEIGHT // 2,BLUE)
        tft.text(small,self.naechste,0,tft.height() // 2 + big.HEIGHT // 2 + small.HEIGHT,GREEN)
        tft.text(big,self.status,0,tft.height()- 2* small.HEIGHT - big.HEIGHT,GREEN)
        tft.text(small,self.unten,0,tft.height() - small.HEIGHT,RED)
        tft.text(small,self.untenRechts,tft.width()-(len(self.untenRechts)) * small.WIDTH,tft.height() - small.HEIGHT,GREEN)
        tft.show()
    def volumenDisplay(self,):
        self.aktuellesMenu='volumen'
        self.menuEbene=2
        self.updatePlayer()
        tft.fill(BACKGROUND)
        maxRechteck=tft.width()-10
        tft.text(big,'Volumen',0,tft.height() // 2 - big.HEIGHT,BLUE)
        tft.rect(10, tft.height() // 2 , tft.width()-20, 20, GREEN)
        tft.fill_rect(10, tft.height() // 2 ,int(maxRechteck* self.volumen/100), 20, GREEN)
        tft.show()
    def frageSonoffAb(self,):
        self.obenLinks=''
        url=f'http{self.sonoff.split("http")[1]}/cm?cmnd=status'
        name=self.sonoff.split("http")[0]
#Testen, ob der Sonoff ueberhaupt an ist.
        try:
            result=uping.ping(url)
        except:
            self.sonoff=''
            return False
        try:
            res=urequests.post(url)
        except:
            self.sonoff=''
            return False
        anAus=ujson.loads(res.text)['Status']['Power']
        self.obenLinks=f'{name}: {"Aus" if anAus=="0" else "An"}'
        return True
    def playUrl(self,url):
        playjson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist","play",url]]})
        res=self.requestsAbfrage(data=playjson,ort='playUrl')
    def playVari(self,vari):
        playjson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],vari]})
        res=self.requestsAbfrage(data=playjson,ort='playVari')
    def setzeZufall(self,zufall=1):
        playjson=ujson.dumps({"id":1,"method":"slim.request","params":[self.players[self.player],["playlist", "shuffle", zufall]]})
        res=self.requestsAbfrage(data=playjson,ort='setzeZufall')
    def requestsAbfrage(self,data=[],ort='Unbekannt',url=''):
        res=-1
        try:
            if len(url)==0:
                url=self.url
            res=urequests.post(url, data = data)
        except:
            print('urequests Fehler in '+str(ort))
        return res

def rfid_read():
    rdr = MFRC522(spi, sda)
    uid = ""
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        global display
        (stat, raw_uid) = rdr.anticoll()
        uresFehler=False
        if stat == rdr.OK:
            uid = ("0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
            statjson=ujson.dumps({"LMS":uid})
            print(statjson)
            try:
                res=urequests.post(parameter.werte('rfid'), data = statjson)
            except:
                uresFehler=True
            print('uid:'+' '+str(uid)+' '+res.text)
            try:
                rueckgabe=ujson.loads(res.text)[uid]
            except:
                if '": ["' in res.text:
                    rueckgabe=res.text.split('": ["')[1]
                    rueckgabe=rueckgabe[:-3]
                else:
                    display.untenRechts="RFID Gesperrt"
                    display.updateDisplay()
                    return False
            print(rueckgabe)
            if  not (uresFehler or ('Not Found' in rueckgabe) or ('Keine Musik' in rueckgabe) or ('Sonoff' in rueckgabe)):
                display.playVari(["playlist","play",rueckgabe])
            if 'Sonoff' in rueckgabe:
                display.sonoff=rueckgabe.split('Sonoff')[1]
            display.untenRechts="RFID Gesperrt"
            display.updateDisplay()
            return False
    return True


display=displayInhalt()
display.updatePlayer()
display.updateDisplay()

def printOnScreen(text='Hello'):
    tft.fill(BACKGROUND)
    tft.text(big,text,0,tft.height() // 2 - big.HEIGHT // 2,RED)
    tft.show()

def main():
    global display
    global statusFailed
    """
    The big show!
    """
    zeitDisUpdate= utime.ticks_ms()
    zeitRfidBlock= utime.ticks_ms()
    rfidFree=True
    try:
        while not statusFailed:
#1. Lese den RFID Kartenleser
            if rfidFree:
                display.untenRechts="RFID Frei"
                rfidFree=rfid_read()
                zeitRfidBlock=utime.ticks_ms()
            else:
                #Blockiere den RFID Scanner fuer 2 s zur Vermeidung von Mehrfachanfragen
                if utime.ticks_ms() - zeitRfidBlock > 2000:
                    rfidFree=True
#2. Aktualisiere jede Sekunde das Display
            if utime.ticks_ms() - zeitDisUpdate > 1000:
                if display.menuEbene < 1:
                    display.updatePlayer()
                    display.ebeneNull()
                zeitDisUpdate=utime.ticks_ms()
#3. Schlafe 100 ms
            time.sleep_ms(100)
    finally:
        printOnScreen('Finally: Fehler, starte neu')
        time.sleep_ms(500)
        tft_config.deinit(tft)
        machine.reset()
    printOnScreen('Fehler, starte neu')
    time.sleep_ms(500)
    tft_config.deinit(tft)
    machine.reset()

main()


