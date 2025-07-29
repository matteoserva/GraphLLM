import os
from glob import glob
import uuid
import re

from modules.executors import get_gui_nodes
from modules.executors.gui_node_builder import GuiNodeBuilder
from .common import HandlerException

SOURCES_PATH="modules/server"
NODES_PATH="modules/gui_nodes"
EXECUTORS_PATH="modules/executors"
LITEGRAPH_PATH = "extras/litegraph.js"

class EditorHandler():
    def __init__(self):
        gui_nodes = [el() for el in get_gui_nodes()]
        for el in gui_nodes:
            setattr(el,"builder",GuiNodeBuilder())
        builders = [el.buildNode() for el in gui_nodes]
        generated_nodes = [{"name": "generated/" + el.config["node_type"] + ".js", "value": el.getNodeString()} for el in builders]

        raw_nodes = []
        node_files = glob(EXECUTORS_PATH + "/*.js")
        node_files.extend(glob(EXECUTORS_PATH + "/*/*.js"))
        for el in node_files:
            with open(el, "r") as f:
                res = f.read()
                base_name = "raw" + el[len(EXECUTORS_PATH):]
                raw_nodes.append({"name": base_name, "value":res})

        self.node_files = raw_nodes + generated_nodes
        self.nodes_map = {el["name"]:el["value"] for el in self.node_files}

    def _returnRedirect(self,server):
        server.send_response(301)
        server.send_header('Location', '/editor/')
        server.end_headers()

    def _do_GET_node(self,server,node_key):
        server.send_response(200)
        server.send_header('Connection', 'close')
        server.send_header('Content-type', 'text/javascript')
        server.end_headers()

        server.wfile.write(self.nodes_map[node_key].encode())

    def _do_GET_litegraph(self,server,endpoint):
        filename = LITEGRAPH_PATH + "/" + endpoint
        if not os.path.isfile(filename):
            raise HandlerException(code=404)
        with open(filename, "rb") as f:
            content = f.read()
            
        server.send_response(200)
        server.end_headers()
        server.wfile.write(content)
        
    def _do_GET_editorFile(self,server,endpoint,content_type='text/javascript'):
        filename = SOURCES_PATH + "/" + endpoint
        if not os.path.isfile(filename):
            raise HandlerException(code=404)
        with open(filename, "rb") as f:
            content = f.read()

        server.send_response(200)
        server.send_header('Content-type', content_type + "; charset=utf-8")
        server.end_headers()
        server.wfile.write(content)

    def do_GET(self, server):
        server.close_connection = True
        http_path = server.path.split("?", 1)[0]
        split_path = http_path.split("/", 2)
        endpoint = split_path[1]

        if re.match(r"^/editor$", http_path):
            return self._returnRedirect(server)
        elif re.match(r"^/editor/node/.*\.js$", http_path):
            return self._do_GET_node(server,http_path[13:])
        elif re.match(r"^/editor/litegraph/js/.*\.js$", http_path):
            return self._do_GET_litegraph(server,"editor/js/" + http_path[21:])
        elif re.match(r"^/editor/litegraph/src/.*\.js$", http_path):
            return self._do_GET_litegraph(server,"src/" + http_path[22:])
        elif re.match(r"^/editor/js/.*\.js(\.map)?$", http_path):
            return self._do_GET_editorFile(server,http_path[8:],content_type='text/plain')

        if endpoint in ["editor"] and len(split_path[2]) == 0:  # index
            filename = SOURCES_PATH + "/" + "index.html"

            myuuid = str(uuid.uuid4())
            text_replacement = '<script type="text/javascript" src="/editor/nodes.js?uuid=' + myuuid + '"></script>'
            text_replacement = '<script type="text/javascript" src="/editor/nodes.js"></script>'

            text_replacement = [f'<script type="text/javascript" src="/editor/node/{el["name"]}"></script>' for el in self.node_files]
            text_replacement = "\n".join(text_replacement)
            content = open(filename, "rb").read()
            content = content.replace(b"<!-- NODE_LIST_PLACEHOLDER -->", text_replacement.encode())

            server.send_response(200)
            server.send_header('Connection', 'close')
            server.send_header('Content-type', 'text/html')
            server.end_headers()
            server.wfile.write(content)

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

            if not content:
                print("-.-----",server.path)
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