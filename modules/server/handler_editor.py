import os
from glob import glob

SOURCES_PATH="modules/server"
NODES_PATH="modules/gui_nodes"
EXECUTORS_PATH="modules/executors"
LITEGRAPH_PATH = "extras/litegraph.js"

class EditorHandler():

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

            node_files = glob(EXECUTORS_PATH + "/*.js")
            node_files.extend(glob(EXECUTORS_PATH + "/*/*.js" ))
            node_files = [el[len(EXECUTORS_PATH)+1:] for el in node_files]
            replaced_node_files = ['<script type="text/javascript" src="nodes/' + el + '"></script>' for el in node_files]
            replaced_text = "\n".join(replaced_node_files)

            content = open(filename, "rb").read()
            content = content.replace(b"<!-- NODE_LIST_PLACEHOLDER -->", replaced_text.encode())

            server.send_response(200)
            server.send_header('Connection', 'close')
            server.send_header('Content-type', 'text/html')
            server.end_headers()
            server.wfile.write(content)

        elif endpoint in ["editor"]:
            remaining = "index.html" if len(split_path[2]) == 0 else split_path[2]
            print(remaining)
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
            # self.send_header('Content-type', 'text/html')
            server.end_headers()
            server.wfile.write(content)
        elif endpoint in ["src", "external", "css", "js", "imgs", "style.css", "examples"]:
            remaining = "/index.html" if len(split_path) < 3 else "/" + split_path[2]

            content = None
            filename = LITEGRAPH_PATH + "/" + endpoint + remaining
            print(filename)
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