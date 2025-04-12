import os
from glob import glob
import uuid

from modules.executors import get_gui_nodes

SOURCES_PATH="modules/server"
NODES_PATH="modules/gui_nodes"
EXECUTORS_PATH="modules/executors"
LITEGRAPH_PATH = "extras/litegraph.js"

class EditorHandler():
    def __init__(self):
        gui_nodes = [el() for el in get_gui_nodes()]
        _ = [el.buildNode() for el in gui_nodes]
        node_strings = [el.getNodeString() for el in gui_nodes]
        self.gui_node_string = "\n\n".join(node_strings)


    def do_GET(self, server):
        server.close_connection = True
        http_path = server.path.split("?", 1)[0]
        split_path = http_path.split("/", 2)
        endpoint = split_path[1]
        if endpoint in ["editor"] and len(split_path) < 3:
            server.send_response(301)
            server.send_header('Location', '/editor/')
            server.end_headers()
            return

        if endpoint in ["editor"] and len(split_path[2]) == 0:  # index
            filename = SOURCES_PATH + "/" + "index.html"

            myuuid = str(uuid.uuid4())
            text_replacement = '<script type="text/javascript" src="/editor/nodes.js?uuid=' + myuuid + '"></script>'
            text_replacement = '<script type="text/javascript" src="/editor/nodes.js"></script>'
            content = open(filename, "rb").read()
            content = content.replace(b"<!-- NODE_LIST_PLACEHOLDER -->", text_replacement.encode())

            server.send_response(200)
            server.send_header('Connection', 'close')
            server.send_header('Content-type', 'text/html')
            server.end_headers()
            server.wfile.write(content)

        elif endpoint in ["editor"] and split_path[2] == "nodes.js":
            server.send_response(200)
            server.send_header('Connection', 'close')
            server.send_header('Content-type', 'text/javascript')
            server.end_headers()

            res = b""
            node_files = glob(EXECUTORS_PATH + "/*.js")
            node_files.extend(glob(EXECUTORS_PATH + "/*/*.js"))
            for el in node_files:
                with open(el,"rb") as f:
                    res += f.read()
                    res += b"\n\n"
            server.wfile.write(res)
            server.wfile.write(self.gui_node_string.encode())

        elif endpoint in ["editor"] and split_path[2] == "img":
            server.send_response(200)
            server.send_header('Connection', 'close')
            server.end_headers()

            content = None
            filename = SOURCES_PATH + "/" + remaining
            if os.path.exists(filename):
                content = open(filename, "rb").read()
            if content:
                server.send_response(200)
                # self.send_header('Content-type', 'text/html')
                server.end_headers()
                server.wfile.write(content)
            else:
                server.send_response(404)
                server.send_header('Content-type', 'text/html')
                server.end_headers()
                server.wfile.write(b'404 - Not Found')

        elif endpoint in ["editor"]:
            remaining = "index.html" if len(split_path[2]) == 0 else split_path[2]
            #print(remaining)
            content = None

            if remaining.startswith("nodes/"):
                filename = EXECUTORS_PATH + "/" + split_path[2].split("/",1)[-1]
                content = open(filename, "rb").read()

            if not content:
                filename = SOURCES_PATH + "/" + remaining
                if os.path.exists(filename):
                    content = open(filename, "rb").read()

            if not content:
                filename = LITEGRAPH_PATH + "/editor/" + remaining
                if content is None and os.path.exists(filename):
                    content = open(filename, "rb").read()

            server.send_response(200)
            server.send_header('Connection', 'close')
            if remaining.endswith(".js"):
                server.send_header('Content-type', 'text/plain; charset=utf-8')
            server.end_headers()
            server.wfile.write(content)
        elif endpoint in ["src", "external", "css", "js", "imgs", "style.css", "examples"]:
            remaining = "/index.html" if len(split_path) < 3 else "/" + split_path[2]

            content = None
            filename = LITEGRAPH_PATH + "/" + endpoint + remaining
            #print(filename)
            if content is None and os.path.isfile(filename):
                content = open(filename, "rb").read()
            if content:
                server.send_response(200)
                # self.send_header('Content-type', 'text/html')
                server.end_headers()
                server.wfile.write(content)
            else:
                server.send_response(404)
                server.send_header('Content-type', 'text/html')
                server.end_headers()
                server.wfile.write(b'404 - Not Found')
        else:
            server.send_response(404)
            server.send_header('Content-type', 'text/html')
            server.end_headers()
            server.wfile.write(b'404 - Not Found')