#!/usr/bin/python3
import sys, signal, time, os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import yaml
from functools import partial
import time
import subprocess

from modules.logging.logger import Logger
from modules.clients import Client, get_client_config
from modules.graph import GraphExecutor
from threading import Thread
from modules.graph.json_parser import JsonParser


class WebExec():
    def __init__(self,send,stop):
        self.t = None
        self.send_chunk = send
        self.send_stop = stop
        client_config = get_client_config()
        client = Client.make_client(client_config)
        client.connect()

        parameters = {}
        parameters["repeat_penalty"] = 1.0
        parameters["penalize_nl"] = False
        parameters["seed"] = -1

        logger= Logger(verbose=False,web_logger = False)
        self.executor_config = {"client":client, "client_parameters":parameters,"logger":logger}


        self.logger = logger
        self.keep_running = False
        self.client = client

    def event(self,t,a,v):
        print(t,a,v)
        res = {"type": t, "data":a}
        resp = json.dumps(res)

        self.send_chunk(resp)

    def _run(self,filename):
        self.logger.addListener(self)
        self.logger.log("start")
        self.executor([])
        self.logger.log("stop")
        self.logger.deleteListeners()
        self.send_stop()


    def start(self,filename):
        args = [filename]

        try:
            self.executor = GraphExecutor(self.executor_config)
            self.executor.load_config(args)
            self.keep_running = True
            self.t = Thread(target=self._run, args=(filename,))
            self.t.start()
        except:
            pass

    def ask_stop(self):
        self.keep_running = False
        try:
            self.executor.stop()
        except:
            pass
    def stop(self):
        self.ask_stop()
        self.t.join()
        self.t = None
    def wait(self):
        if(self.t):
            self.t.join()
        self.t = None
    def run(self,filename):
        self.start(filename)
        self.wait()


class ModelHandler():
    def __init__(self):
        self.index = 1

    def send_prompt(self):
        self.server.send_response(200)
        self.server.end_headers()
        
        content_length = int(self.server.headers['Content-Length'])
        post_data = self.server.rfile.read(content_length)
        with open("/tmp/grah.json","w") as f:
             a = json.loads(post_data)
             f.write(json.dumps(a,indent=4))
        v2="ciao"
        self.server.wfile.write(v2.encode('utf-8'))
        self.index += 1

    def save(self,post_data):
        with open("/tmp/graph.json", "w") as f:
            a = json.loads(post_data)
            f.write(json.dumps(a, indent=4))
        self.server.send_response(200)
        self.server.end_headers()
        self.server.wfile.write("ciao".encode())
        return "ciao"

    def test(self):
        self.server.close_connection = False
        self.server.send_response(200)
        self.server.send_header('Content-type', 'application/json')
        self.server.send_header('transfer-encoding', 'chunked')
        self.server.end_headers()
        for i in range(10):
            res = {"content": [str(i)]}
            resp = json.dumps(res)
            resp = "{}\n\n".format(resp)
            l = len(resp)
            encoded = '{:X}\r\n{}\r\n'.format(l, resp).encode('utf-8')
            res = self.server.wfile.write(encoded)
            time.sleep(.4)
        close_chunk = '0\r\n\r\n'
        self.server.wfile.write(close_chunk.encode(encoding='utf-8'))
        self.server.wfile.flush()
        self.server.close_connection = True

    def _send_chunk(self,chunk):
        resp = "{}\n\n".format(chunk)
        l = len(resp)
        encoded = '{:X}\r\n{}\r\n'.format(l, resp).encode('utf-8')
        res = self.server.wfile.write(encoded)

    def _send_stop(self):
        close_chunk = '0\r\n\r\n'
        self.server.wfile.write(close_chunk.encode(encoding='utf-8'))
        self.server.wfile.flush()


    def exec(self,json_graph):
        self.server.close_connection = False
        self.server.send_response(200)
        self.server.send_header('Content-type', 'application/json')
        self.server.send_header('transfer-encoding', 'chunked')
        self.server.end_headers()
        with open("/tmp/graph.json", "w") as f:
            a = json.loads(json_graph)
            f.write(json.dumps(a, indent=4))
        parser = JsonParser()
        parsed = parser.load("/tmp/graph.json")
        with open("/tmp/graph.yaml", "w") as f:
            f.write(yaml.dump(parsed, sort_keys=False))
        e = WebExec(self._send_chunk, self._send_stop)
        e.run("/tmp/graph.yaml")

        self.server.close_connection = True

class HttpHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def __init__(self, model, *args, **kwargs):
        self.model = model
        self.model.server = self
        
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.close_connection = True
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

        #print(http_path)
        if endpoint in ["graph"]:
            http_path = self.path.split("?", 1)[0]
            split_path = http_path.split("/", 2)
            if len(split_path) < 3 or len(split_path[2]) < 1:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'404 - Not Found')

            operation = split_path[2]
            if hasattr(self.model, operation):
                op = getattr(self.model, operation)
                res = op()

            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'404 - Not Found')
            pass

        elif endpoint in ["editor"] :
            remaining = "index.html" if len(split_path[2]) == 0 else split_path[2]
            print(remaining)
            content = None

            filename = "extras/web_bridge/" + remaining
            if os.path.exists(filename):
                content = open(filename,"rb").read()
            filename = "extras/litegraph.js/editor/"  + remaining
            if content is None and os.path.exists(filename):
                content = open(filename,"rb").read()

            self.send_response(200)
            self.send_header('Connection', 'close')
                #self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        elif endpoint in ["src","external","css","js","imgs","style.css","examples"]:
            remaining = "/index.html" if len(split_path) < 3 else "/" + split_path[2]
            
            content = None
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
        self.close_connection = True
        http_path = self.path.split("?", 1)[0]
        split_path = http_path.split("/", 2)
        operation = split_path[2]
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        if hasattr(self.model,operation):

            op = getattr(self.model,operation)
            res = op(post_data)

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 - Not Found')
        pass

            
if __name__ == '__main__':


    model_handler = ModelHandler()
    http_handler = partial(HttpHandler, model_handler)
    http_server = HTTPServer(('0.0.0.0', 8008), http_handler)
    print("server listening at http://localhost:8008/")


    def handler(signal_received, frame):
        print("Handler called\n")
        #http_server.shutdown()
        sys.exit(0)


    signal.signal(signal.SIGINT, handler)



    http_server.serve_forever()
    http_server.shutdown()