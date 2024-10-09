import sys, signal, time, os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from functools import partial
import time
import subprocess

class ModelHandler():
    def __init__(self):
        self.index = 1

    def send_prompt(self):
        self.server.send_response(200)
            #self.send_header('Content-type', 'text/html')
        self.server.end_headers()
        fullargs = ["python3", "exec.py", "-j", "graphs/run_template.txt","examples/template_full.txt"]
        result = subprocess.run(fullargs, capture_output=True, text=True, input="")
        last_row = result.stdout.strip().split("\n")[-1]
        v1 = json.loads(last_row)
        v2 = v1[0]
        print(v2)
        self.server.wfile.write(v2.encode('utf-8'))
        self.index += 1


class HttpHandler(BaseHTTPRequestHandler):
    #protocol_version = 'HTTP/1.1'
    def __init__(self, model, *args, **kwargs):
        self.model = model
        self.model.server = self
        
        super().__init__(*args, **kwargs)

    def do_GET(self):
        http_path = self.path.split("?",1)[0]
        
        if http_path == "/":
            self.send_response(301)
            self.send_header('Location','/editor/')
            self.end_headers()
            return
        split_path = http_path.split("/",2)
        
        endpoint = split_path[1]
        if endpoint in ["editor"] and len(split_path) < 3:
            self.send_response(301)
            self.send_header('Location','/editor/')
            self.end_headers()
            return
        remaining = "index.html" if len(split_path[2]) == 0 else split_path[2]
        
        #print(http_path)
        if endpoint in ["graph"]:
            self.model.send_prompt()
        
        elif endpoint in ["editor"] and remaining in ["index.html","bridge.js"]:
            
            print(remaining)
            filename = "extras/web_bridge/" + remaining
            content = open(filename,"rb").read()
            self.send_response(200)
                #self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        elif endpoint in ["editor","src","external","css","js","imgs","style.css","examples"]:
            remaining = "/index.html" if len(split_path) < 3 else "/" + split_path[2]
            
            content = None
            filename = "extras/litegraph.js/editor"  + remaining
            if os.path.isfile(filename):
                content = open(filename,"rb").read()
            filename = "extras/litegraph.js/" + endpoint + remaining
            print(filename)
            if content is None and os.path.isfile(filename):
                content = open(filename,"rb").read()
            if content:
                self.send_response(200)
                #self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'404 - Not Found')
        else:
             self.send_response(404)
             self.send_header('Content-type', 'text/html')
             self.end_headers()
             self.wfile.write(b'404 - Not Found')
    def do_POST(self):
        print(self.path)
        self.model.send_prompt()


            
if __name__ == '__main__':


    model_handler = ModelHandler()
    http_handler = partial(HttpHandler, model_handler)
    http_server = HTTPServer(('0.0.0.0', 8008), http_handler)



    def handler(signal_received, frame):
        print("Handler called\n")
        #http_server.shutdown()
        sys.exit(0)


    signal.signal(signal.SIGINT, handler)



    http_server.serve_forever()
    http_server.shutdown()
