import json
import os
import tempfile
import time

import yaml
from modules.graph.json_parser import JsonParser
from modules.server.handler_exec import WebExec


class ModelHandler():
    def __init__(self,blob):
        self.index = 1
        self.blob = blob

    def send_prompt(self):
        self.server.send_response(200)
        self.server.end_headers()

        content_length = int(self.server.headers['Content-Length'])
        post_data = self.server.rfile.read(content_length)
        with open(tempfile.gettempdir() +"/grah.json","w") as f:
             a = json.loads(post_data)
             f.write(json.dumps(a,indent=4))
        v2="ciao"
        self.server.wfile.write(v2.encode('utf-8'))
        self.index += 1

    def _is_valid_filename(self, filename):
        if len(filename) > 1 and filename != "Empty" and filename.find("/") < 0 and filename.find(".") < 0:
             return True
        return False

    def save(self,post_data):
        params = self.server.path.split("?", 1)[-1]
        filename = params.split("=")[1]

        with open(tempfile.gettempdir() + "/graph.json", "w") as f:
            a = json.loads(post_data)
            f.write(json.dumps(a, indent=4))
        if self._is_valid_filename(filename):
            with open("json_graphs/" +filename + ".json", "w") as f:
                a = json.loads(post_data)
                f.write(json.dumps(a, indent=4))
        self.server.send_response(200)
        self.server.send_header("Content-type","text/plain")
        self.server.end_headers()
        self.server.wfile.write("ciao".encode())
        return "ciao"

    def delete(self,post_data):
        params = self.server.path.split("?", 1)[-1]
        filename = params.split("=")[1]

        if self._is_valid_filename(filename):
            full_name = "json_graphs/" +filename + ".json"
            os.remove(full_name)
        self.server.send_response(200)
        self.server.send_header("Content-type","text/plain")
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
        chunk += "\n"
        resp = chunk.encode()
        l = len(resp)
        encoded = "{:X}\r\n".format(l).encode() + resp + b"\r\n"
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
        with open(tempfile.gettempdir() + "/graph.json", "w") as f:
            a = json.loads(json_graph)
            f.write(json.dumps(a, indent=4))
        parser = JsonParser()
        parsed = parser.load(tempfile.gettempdir() + "/graph.json")
        with open(tempfile.gettempdir() + "/graph.yaml", "w") as f:
            f.write(yaml.dump(parsed, sort_keys=False))
        e = WebExec(self._send_chunk,self.blob)
        e.run(tempfile.gettempdir() + "/graph.yaml")
        try:
            self._send_stop()
        except:
            pass

        self.server.close_connection = True

    def load(self):
        self.server.send_response(200)
        self.server.send_header('Content-type', 'application/json')
        self.server.end_headers()
        params = self.server.path.split("?",1)[1]
        filename = params.split("=")[1]
        with open("json_graphs/" + filename+".json") as f:
            content = f.read()
        self.server.wfile.write(content.encode())

    def _list_files_recursive(self, outval, base_path, current_path=''):
        path = os.path.join(base_path ,current_path)
        for entry in os.listdir(path):
            entry_path = os.path.join(current_path, entry)
            full_path = os.path.join(base_path,entry_path)
            if os.path.isdir(full_path):
                self._list_files_recursive(outval, base_path, entry_path)
            else:
                outval.append(entry_path)

    def list(self):
        self.server.send_response(200)
        self.server.send_header("Content-type","text/plain")
        self.server.end_headers()
        files = []
        self._list_files_recursive(files, "json_graphs/")
        files = [el[:-5] for el in files if el.endswith(".json")]
        files = sorted(files)
        text = "\n".join(files)
        self.server.wfile.write(text.encode())