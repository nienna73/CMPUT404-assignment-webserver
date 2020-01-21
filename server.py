#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    file_path = 'www'
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data.decode('utf-8'))
        decoded_data = self.data.decode('utf-8')
        split_data = decoded_data.split('\n')
        req_url = split_data[0].split()[1]
        req_method = split_data[0].split()[0]

        if req_method != "GET":
            self.request.send("405".encode('utf-8'))
            return

        self.serve_page(req_url)

    def serve_page(self, url):
        print("\n\nURL ==== " + url + '\n\n')
        if url == '/favicon.ico':
            return
        #referencing: https://stackoverflow.com/questions/36122461/trying-to-send-http-response-from-low-level-socket-server
        local_file_path = self.file_path + url
        if os.path.exists(local_file_path):
            if local_file_path[-1] == '/':
                local_file_path = local_file_path + "index.html"
        
            with open(local_file_path) as f:
                data = f.read()
                response_headers = {
                    'Content-Type': 'text/html; encoding=utf8' if ".html" in local_file_path else 'text/css; encoding=utf8',
                    'Content-Length': len(data),
                    'Connection': 'close',
                }

                response_headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in response_headers.items())

                response_proto = 'HTTP/1.1'
                response_status = '200'
                response_status_text = 'OK' # this can be random

                # sending all this stuff
                r = '%s %s %s\r\n' % (response_proto, response_status, response_status_text)
                self.request.send(r.encode('utf-8'))
                self.request.send(response_headers_raw.encode('utf-8'))
                self.request.send('\r\n'.encode('utf-8')) # to separate headers from body
                self.request.send(data.encode('utf-8'))

                self.request.sendall(bytearray("OK",'utf-8'))

        else:
            self.request.send("404".encode('utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8081

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
