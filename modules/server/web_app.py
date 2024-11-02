#!/usr/bin/python3
import sys, signal, os
from http.server import HTTPServer,ThreadingHTTPServer, BaseHTTPRequestHandler
from functools import partial

from modules.server.handler_exec import ExecHandler
from modules.server.handler_model import ModelHandler
from modules.server.handler_editor import EditorHandler
from modules.server.handler_blob import BlobHandler

class HttpDispatcher:

    def __init__(self, *args, **kwargs):

        self.editor = EditorHandler()
        self.blob = BlobHandler()
        self.model = ModelHandler(self.blob)

    def do_GET(self,server):
        self.model.server = server
        server.close_connection = True
        http_path = server.path.split("?",1)[0]

        if http_path == "/":
            server.send_response(301)
            server.send_header('Location','/editor/')
            server.end_headers()
            return
        split_path = http_path.split("/",2)

        endpoint = split_path[1]

        if endpoint in ["graph"]:
            http_path = server.path.split("?", 1)[0]
            split_path = http_path.split("/", 2)
            if len(split_path) < 3 or len(split_path[2]) < 1:
                server.send_response(404)
                server.send_header('Content-type', 'text/html')
                server.end_headers()
                server.wfile.write(b'404 - Not Found')

            operation = split_path[2]
            if server.headers.get("Upgrade", None) == "websocket":
                wsExec = ExecHandler(server,self.blob)
                op = getattr(wsExec,operation)
                res = op()
            elif hasattr(self.model, operation):
                op = getattr(self.model, operation)
                res = op()

            else:
                server.send_response(404)
                server.send_header('Content-type', 'text/html')
                server.end_headers()
                server.wfile.write(b'404 - Not Found')
            pass

        elif endpoint in ["editor","src","external","css","js","imgs","style.css","examples"]:
            handler = self.editor
            return handler.do_GET(server)
        elif endpoint in ["blob"] and len(split_path) >= 3 and len(split_path[2]) > 0:
            return self.blob.do_GET(server)
        else:
             server.send_response(404)
             server.send_header('Content-type', 'text/html')
             server.end_headers()
             server.wfile.write(b'404 - Not Found')

    def do_POST(self,server):
        self.model.server = server
        server.close_connection = True
        http_path = server.path.split("?", 1)[0]
        split_path = http_path.split("/", 2)
        operation = split_path[2]
        content_length = int(server.headers['Content-Length'])
        post_data = server.rfile.read(content_length)
        if hasattr(self.model,operation):

            op = getattr(self.model,operation)
            res = op(post_data)

        else:
            server.send_response(404)
            server.send_header('Content-type', 'text/html')
            server.end_headers()
            server.wfile.write(b'404 - Not Found')
        pass

class HttpServerWrapper(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __init__(self, dispatcher, *args, **kwargs):
        self.dispatcher = dispatcher
        super().__init__(*args, **kwargs)

    def do_GET(self):
        return self.dispatcher.do_GET(self)

    def do_POST(self):
        return self.dispatcher.do_POST(self)



def run():
    http_dispatcher = HttpDispatcher()
    http_wrapper = partial(HttpServerWrapper, http_dispatcher)
    http_server = ThreadingHTTPServer(('0.0.0.0', 8008), http_wrapper)
    print("server listening at http://localhost:8008/")

    def handler(signal_received, frame):
        print("Handler called\n")
        # http_server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    http_server.serve_forever()
    http_server.shutdown()

if __name__ == '__main__':
    run()


