# Den Logitech Media Server mit RFID Karten steuern


## Inhalt

## Vorbemerkung
Den Logitech Media Server kann man gut mit Handy und Browser fernsteuern. Doch habe ich nicht immer mein Handy dabei und möchte auch gerne, dass meine Kinder selbständig Lieder und Hörbücher starten können. Für letzteres gibt es auch gute eigenständige Systeme, wie z.B. der TonUINO, aber gerade für ältere Kinder ist dies irgendwann nicht mehr zeitgemäß. Da ich selber schon länger den Logitech Media Server (LMS) nutze und meinen Kinder den irgendwann auch in deren Zimmer einbauen wollte, entschied ich mich, mir eine RFID - Steuerung für diesen einzurichten.

##Aufbau
Aus folgenden drei Komponenten besteht ein komplettes System


1. Server mit einer laufenden LMS Instanz. ([Ich nutze Docker](https://hub.docker.com/r/lmscommunity/lyrionmusicserver))
2. Einen Clienten, der die Musik wiedergibt. ([Ich nutze squeezelite-esp32](https://github.com/sle118/squeezelite-esp32))
3. Die hier vorgestellte RFID-Steuerung.

##RFID Steuerung auf ESP32-Display

##Komponenten

* T-Display-S3 ESP32 S3 with 1.9 inch ST7789 LCD Display
* MFRC-522 Mini RC522
* Key Button Membrane Switch 3 ([Color: 5key-matrix-keyboard](https://www.aliexpress.com/item/1005004528531101.html))
* USB Schalter
* USB Powerbank

###Firmware flashen
```
pip install esptool
esptool.py --chip esp32s3 --port /dev/ttyACM0 erase_flash
esptool.py --chip esp32s3 --port /dev/ttyACM0 write_flash -z 0 ep32-S3_display_firmware.bin
```

###LMS-Steuerung aufs Display laden
Zur Übertragung des Skripts auf das ESP32 Display benutze ich Thonny. Wähle Run --> Select Interpreter --> Micropython (ESP32) und suche dann den richtigen Port. Speicher damit *squeezeplayerSteuerung.py* auf dem Display.

###LMS-Steuerung anpassen
Rufe das Skript *paramter.py* in Thonny auf und passe folgende Angaben an:

* wlanname
* wlanpasswort
* squeezeclient
* lmsserverip
* rfidserverip

Speicher dann *parameter.py* auf dem Display

![Bild 1](bilder/thonny_3_WhereToSave.png")

###Komponenten Verbinden

##Installation restlicher Komponenten

### LMS Server
Zur Docker-Installation kopiere dir die Docker-Compose Datei auf deinen Server und starte diesen mit 
```
docker-compose up -d
```
###squeezelite-esp32
Für den Clienten braucht man folgende Teile:

1. ESP32-S3 Development Board (z.B. von Aliexpress)
2. DAC Module 1334 UDA1334A I2S DAC (z.B. von Aliexpress)
3. SONOFF Basic R2
4. USB Netzteil
5. USB Splitter, Eins auf Zwei
6. USB Boxen
7. 3.5mm Audio Aux Cable Anti-interference Ground Loop Noise Filter

#### ESP32-S3 Installation
**Softwareinstallation**
```
mkdir ~/esp
cd ~/esp
git clone -b v4.4.4 --recursive https://github.com/espressif/esp-idf.git esp-idf-v4.4
/home/jochen/esp/esp-idf-v4.4/install.sh
. /home/jochen/esp/esp-idf-v4.4/export.sh
git clone --recursive https://github.com/sle118/squeezelite-esp32.git

```
**ESP32-S3 Flashen**
Passe mit dem Befehl "idf.py menuconfig" folgende Einstellungen an.

![Bild 1](bilder/squeezeplayer_1_serialFlashConfig.png "Serial Flasher config")
![Bild 2](bilder/squeezeplayer_2_squeezelite-esp32_AudioInput.png "Serial Flasher config")
![Bild 3](bilder/squeezeplayer_3_componente-config_Bluetooth.png "")
![Bild 4](bilder/squeezeplayer_4-0_componente-config_Esp32S3-Specific.png "")
![Bild 5](bilder/squeezeplayer_4-1_componente-config_Esp32S3-Specific.png "")
![Bild 6](bilder/squeezeplayer_4-2_componente-config_Esp32S3-Specific.png "")
![Bild 7](bilder/squeezeplayer_5_componente-config_FreeRTOS.png "")

Führe dann folgende Befehle aus:
```
idf.py build
idf.py flash
```

**ESP32-S3 mit DAC verbinden**

Verlöten folgende Punkte zwischen dem ESP und dem DAC

| ESP32-S3    | DAC 1334|
| -------- | ------- |
| V3.3 | V3.3 |
| GND | GND     |
|  42 | WSEL    |
|  41 | DIN |
|  40 | BCLK

**ESP32-S3 Einrichten**

Verbinde dich mit dem ESP32-S3 mit dem Handy, WLAN squeezelite-esp32, Passwort squeezelite



