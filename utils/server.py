import sys, signal, time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from functools import partial
from client_glm import GLMClient


server_props=b"""{
  "system_prompt": "",
  "default_generation_settings": {
    "n_ctx": 8192,
    "n_predict": -1,
    "model": "GLM-4-9b-chat",
    "seed": -1,
    "temperature": 0.800000011920929,
    "dynatemp_range": 0,
    "dynatemp_exponent": 1,
    "top_k": 40,
    "top_p": 0.949999988079071,
    "min_p": 0.0500000007450581,
    "tfs_z": 1,
    "typical_p": 1,
    "repeat_last_n": 64,
    "repeat_penalty": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "penalty_prompt_tokens": [],
    "use_penalty_prompt_tokens": false,
    "mirostat": 0,
    "mirostat_tau": 5,
    "mirostat_eta": 0.100000001490116,
    "penalize_nl": false,
    "stop": [],
    "n_keep": 0,
    "n_discard": 0,
    "ignore_eos": false,
    "stream": true,
    "logit_bias": [],
    "n_probs": 0,
    "min_keep": 0,
    "grammar": "",
    "samplers": [
      "top_k",
      "tfs_z",
      "typical_p",
      "top_p",
      "min_p",
      "temperature"
    ]
  },
  "total_slots": 1
}"""

class ModelHandler():
    def __init__(self):
        self.model = GLMClient()
        self.model.connect()

    def get_props(self):
        server = self.server
        self.server.send_response(200)
        self.server.send_header('Content-type', 'application/json')
        self.server.end_headers()
        self.server.wfile.write(server_props)
        #server.wfile.flush()
        server.close_connection = True
        pass
        #server.finish()
        #server.connection.close()

    def tokenize(self,obj):
        server = self.server
        server.send_response(200)
        server.send_header('Content-type', 'application/json')
        server.end_headers()
        value = obj["content"]
        tokens = self.model.tokenize(value)
        res = {"tokens":tokens}
        server.wfile.write(json.dumps(res).encode())
        server.close_connection = True
        #server.wfile.flush()
        #server.finish()

    def send_prompt(self,obj):
        server = self.server
        server.send_response(200)
        server.send_header('Content-type', 'application/json')
        server.send_header('transfer-encoding', 'chunked')
        server.end_headers()

        prompt = obj["prompt"]
        res = self.model.send_prompt(prompt)

        for token in res:
            res = {"content": token}
            resp =json.dumps(res)
            resp= "data: {}\n\n".format(resp)
            l = len(resp)
            encoded = '{:X}\r\n{}\r\n'.format(l, resp).encode('utf-8')
            server.wfile.write(encoded)
        close_chunk = '0\r\n\r\n'
        server.wfile.write(close_chunk.encode(encoding='utf-8'))
        server.close_connection = True


class HttpHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def __init__(self, model, *args, **kwargs):
        self.model = model
        self.model.server = self
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.model.get_props()


    def do_POST(self):
        print(self.path)
        args = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')
        try:
            obj = json.loads(args)
            print(obj)
        except:
            self.send_error(404, 'BAD REQ')
            return
        path = self.path.split("/")[-1]
        if path=="tokenize":
            self.model.tokenize(obj)
        elif path == "completion":
            self.model.send_prompt(obj)
        else:
            self.send_error(404, 'BAD REQ')


if __name__ == '__main__':


    ARG_SEP = '---'

    args = sys.argv[1:]
    if len(args) < 1:
        print(f"usage: python openai_api.py path/to/chat/model path/to/fim/model [more args for chat model {ARG_SEP} more args for fim model]")
        exit(-1)

    chat_args = args[2:]
    fim_args = []
    if ARG_SEP in chat_args:
        i = chat_args.index(ARG_SEP)
        fim_args = chat_args[i + 1:]
        chat_args = chat_args[:i]

    basic_args = ['-i', '-m']

    model_handler = ModelHandler()
    http_handler = partial(HttpHandler, model_handler)
    http_server = HTTPServer(('0.0.0.0', 8080), http_handler)



    def handler(signal_received, frame):
        http_server.shutdown()
        sys.exit(0)


    #signal.signal(signal.SIGINT, handler)



    http_server.serve_forever()
    http_server.shutdown()