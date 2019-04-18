#!/usr/bin/env python3

from rofidrop import show_recieve_dialog, path_dialog_loop
 
import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
import json
from io import BytesIO
 
 
class RdListener(http.server.BaseHTTPRequestHandler):
    server_version = "SimpleFileUploadServer/2"
 
    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        resp = {"info": info}
        if r:
            resp['status'] = "OK"
        else:
            resp['status'] = "FAIL"
        f = BytesIO()
        json_resp = json.dumps(resp)
        f.write(str.encode(json_resp))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
        
    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
            
        write_path = self.handle_file_request({"name": fn})
        if write_path == False:
            return (False, "Server refused your request")
        fn = os.path.join(write_path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        print(fn)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")
                
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")
 
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def handle_file_request(self, file):
        choice = show_recieve_dialog(file)
        if choice == "Save":
            return os.environ["HOME"]
        if choice == "Save As":
            return path_dialog_loop(file, os.environ["HOME"])
        if choice == "Ignore":
            return False



def start_server(HandlerClass = RdListener, ServerClass = http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)
 
if __name__ == '__main__':
    start_server()