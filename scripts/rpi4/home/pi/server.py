#! /usr/bin/python3

from os import curdir
from os.path import join as pjoin

from http.server import BaseHTTPRequestHandler, HTTPServer

class StoreHandler(BaseHTTPRequestHandler):
      store_path1 = pjoin(curdir, 'axpert.json')
      store_path2 = pjoin(curdir, 'controller.json')

      def _send_cors_headers(self):
         self.send_header("Access-Control-Allow-Origin", "127.0.0.1:3000")
         self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
         self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type,DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range")
         self.send_header("Access-Control-Allow-Credentials", "true")
         self.send_header("Access-Control-Max-Age", "1728000")


      def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

      def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if self.path == '/axpert.json':
             with open(self.store_path1) as fh:
                self.send_header('Content-type', 'text/json')
                self.wfile.write(fh.read().encode())

        if self.path == '/controller.json':
             with open(self.store_path2) as fh:
                self.send_header('Content-type', 'text/json')
                self.wfile.write(fh.read().encode())

      def do_POST(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if self.path == '/axpert.json':
            length = self.headers['Content-length']
            data = self.rfile.read(int(length))

            with open(self.store_path1, 'w') as fh:
                fh.write(data.decode())

        if self.path == '/controller.json':
            length = self.headers['Content-length']
            data = self.rfile.read(int(length))

            with open(self.store_path2, 'w') as fh:
                fh.write(data.decode())


server = HTTPServer(('', 48211), StoreHandler)
server.serve_forever()

