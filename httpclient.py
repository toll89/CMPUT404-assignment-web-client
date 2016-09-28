
# coding: utf-8
# Copyright 2016 Jarrett Toll
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from urlparse import urlparse
import re
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code, body):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsock.connect((host, int(port)))
        return clientsock

    def get_code(self, data):
        statusline = data.splitlines()[0]
        statuscode = statusline.split()[1]
        return statuscode

    def get_headers(self,data):
        statusheaders = re.split("\r\n\r\n", data)[0]
        headers = statusheaders.partition("\r\n")[2]
        return headers

    def get_body(self, data):
        if data:
            body = re.split("\r\n\r\n", data)[1]
        else:
            body = None
        return body

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        urlpar = urlparse(url)
        if "www." in urlpar.hostname:
            host = urlpar.hostname[4:]
        else:
            host = urlpar.hostname

        if urlpar.port:
            port = urlpar.port
        else:
            port = 80

        sock = HTTPClient().connect( host, port)
        sock.send("GET %s HTTP/1.1\r\n" % urlpar.path)
        sock.send("Host: %s\r\n" % host)
        sock.send("Accept: */*\r\n\r\n")

        response = self.recvall(sock)
        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
        return HTTPResponse(int(code), body)

    def POST(self, url, args=None):
        urlpar = urlparse(url)
        if "www." in urlpar.hostname:
            host = urlpar.hostname[4:]
        else:
            host = urlpar.hostname
        if urlpar.port:
            port = urlpar.port
        else:
            port = 80
        if args:
            encoded = urllib.urlencode(args)
            length = len(encoded)
       
        sockpost = HTTPClient().connect(host, port)
        sockpost.send("POST %s HTTP/1.1\r\n" % urlpar.path)
        if args:
            sockpost.send("Content-Length: %d\r\n" % int(length))
        else:
            sockpost.send("Content-Length: 0\r\n")
        sockpost.send("Host: %s\r\n" % host)
        sockpost.send("Accept: */*\r\n")
        sockpost.send("Content-Type: application/x-www-form-urlencoded\r\n")    
        sockpost.send("\r\n")
        if args:
            sockpost.send(encoded)

        response = self.recvall(sockpost)
        code = self.get_code(response)
        body = self.get_body(response)      
        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
