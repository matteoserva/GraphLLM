
import json
import requests
from . import common
from .common import get_formatter,build_prompt
from .formatter import Formatter

class Client:
    def __init__(self,host="minipd"):
        self.host = host
        self.parameters = {}

    def connect(self):
        props = self.get_server_props()
        model_path = props["default_generation_settings"]["model"]
        model_name = model_path.split("/")[-1]
        self.model_name = model_name
        self.formatter = Formatter()
        self.formatter.load_model(model_name)
        #get_formatter(props)

    def set_parameters(self,parameters):
        self.parameters = parameters

    def get_model_name(self):
        return self.model_name

    def get_server_props(self):
        url = "http://" + self.host + ":8080/props"
        r = requests.get(url)
        resp = json.loads(r.content)
        return resp

    def ricevi(self,r1):
        a = 1
        for line in r1.iter_lines():
            # filter out keep-alive new lines
            a = a + 1
            if line:
                decoded_line = line.decode('utf-8')
                json_decoded = json.loads(decoded_line[6:])
                #print(json_decoded)
                yield json_decoded["content"]


    def _send_prompt_text(self, p, params):
        a={}
        a["n_predict"] = 128*8
        a["stop"] = ["<|end|>","<|im_end|>"]
#        a["temperature"] = 0.0
        a["seed"] = 0
        a["cache_prompt"] = True
        a["stream"] = True
        #a["top_k"] = 5

        for el in params:
            if el == "stop":
                a["stop"].extend(params[el])
            else:
                a[el] = params[el]
        a["prompt"] = p

        #a = {"messages":p}
        js = json.dumps(a)
        #print(a,"\n-\n" + p + "-")
        url = "http://" + self.host + ":8080/completion"
        headers = {"Content-Type": "application/json"}

        data = js
        r = requests.post(url,data=data,headers=headers,stream=True)
        g = self.ricevi(r)
        return g

    def _send_prompt_builder(self,p,params):
        prompt = p._build()
        return self._send_prompt_text(prompt,params)

    def apply_format_templates(self,prompt):
        return self.formatter.apply_format_templates(prompt)

    def send_prompt(self,p,params=None):
        if params is None:
            params = self.parameters
        if isinstance(p,str):
            return self._send_prompt_text(p,params)
        else:
            return self._send_prompt_builder(p,params)
