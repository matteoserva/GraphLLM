#!/usr/bin/python3
import sys, signal, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import partial

from modules.server.handler_exec import ExecHandler
from modules.server.handler_model import ModelHandler

SOURCES_PATH="modules/server"
NODES_PATH="modules/gui_nodes"
LITEGRAPH_PATH = "extras/litegraph.js"


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
            if self.headers.get("Upgrade", None) == "websocket":
                wsExec = ExecHandler(self)
                op = getattr(wsExec,operation)
                res = op()
            elif hasattr(self.model, operation):
                op = getattr(self.model, operation)
                res = op()

            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'404 - Not Found')
            pass

        elif endpoint in ["editor"] and len(split_path[2]) == 0: #index
            filename = SOURCES_PATH + "/" + "index.html"

            node_files = os.listdir(NODES_PATH)
            node_files = [el for el in node_files if el.endswith(".js")]
            node_files = sorted(node_files)

            replaced_node_files = ['<script type="text/javascript" src="nodes/' + el + '"></script>' for el in node_files]
            replaced_text = "\n".join(replaced_node_files)

            content = open(filename, "rb").read()
            content = content.replace(b"<!-- NODE_LIST_PLACEHOLDER -->",replaced_text.encode())

            self.send_response(200)
            self.send_header('Connection', 'close')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)

        elif endpoint in ["editor"] :
            remaining = "index.html" if len(split_path[2]) == 0 else split_path[2]
            print(remaining)
            content = None

            if remaining.startswith("nodes/"):
                filename = NODES_PATH + "/" + split_path[2].split("/")[-1]
                content = open(filename, "rb").read()

            if not content:
                filename = SOURCES_PATH + "/" + remaining
                if os.path.exists(filename):
                    content = open(filename,"rb").read()

            if not content:
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

def run():
    model_handler = ModelHandler()
    http_handler = partial(HttpHandler, model_handler)
    http_server = HTTPServer(('0.0.0.0', 8008), http_handler)
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


