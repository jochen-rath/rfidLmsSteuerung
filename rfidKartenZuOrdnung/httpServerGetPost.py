#!/usr/bin/env python3
"""An example HTTP server with GET and POST endpoints."""

from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import json
import time
import csv
import requests

# Sample blog post data similar to
# https://ordina-jworks.github.io/frontend/2019/03/04/vue-with-typescript.html#4-how-to-write-your-first-component
def leseRfidKartenDatei():
    with open('rfidKarten.csv') as csvfile:
        s = csv.reader(csvfile, delimiter=',')
        inhalt = list(s)
    karten={}
    for zeile in inhalt[1:]:
        karten[zeile[0]]=zeile[1:]
    return karten

class _RequestHandler(BaseHTTPRequestHandler):
    # Borrowing from https://gist.github.com/nitaku/10d0662536f37a087e1b
    def _set_headers(self):
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin, so CORS policies don't
        # prevent local development.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'Unbekannt': 'Bitte RFID Nummer angeben'}).encode('utf-8'))

    def do_POST(self):
        karten=leseRfidKartenDatei()
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        self._set_headers()
        if list(message.keys())[0]=='LMS':
            if message["LMS"] in karten.keys():
                if karten[message["LMS"]][0].startswith('Sonoff'):
                    url=f'http{karten[message["LMS"]][0].split("http")[1]}'
                    res=requests.get(url)
                    self.wfile.write(json.dumps({message['LMS']: 'Keine Musik'}).encode('utf-8'))
                else:
                    self.wfile.write(json.dumps({message['LMS']: karten[message["LMS"]]}).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({message['LMS']: F'Not Found'}).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({'Unbekannt': 'Bitte RFID Nummer angeben'}).encode('utf-8'))
                

#curl http://localhost:8001
#curl --data "{\"this\":\"is a test\"}"  http://localhost:8001
#curl --data "{\"RFID\":\"code\"}"  http://localhost:8001
#curl --data "{\"RFID\":\"46345\"}"  http://localhost:8001
def run_server():
    server_address = ('', 8001)
    httpd = HTTPServer(server_address, _RequestHandler)
    print('serving at %s:%d' % server_address)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
