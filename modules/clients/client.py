
import json
import requests
#from . import common
from ..common import get_formatter,build_prompt,merge_params
from ..formatter import Formatter
import time
import copy
from threading import BoundedSemaphore

DEFAULT_HOST="minipd"

class ONNXClient(object):
    def __new__(cls, *args,**kwargs):
        print("loading subonnx")
        try:
           retval = object.__new__(ONNXClientInner,*args,**kwargs)
        except:
           from .client_onnx import ONNXClient as ONNXClientInner
           retval = object.__new__(ONNXClientInner,*args,**kwargs)
        retval.__init__(*args,**kwargs)
        return retval

class GLMClient(object):
    def __new__(cls, *args,**kwargs):
        print("loading subglm")
        try:
           retval = object.__new__(GLMClientInner,*args,**kwargs)
        except:
           from .client_glm import GLMClient as GLMClientInner
           retval = object.__new__(GLMClientInner,*args,**kwargs)
        retval.__init__(*args,**kwargs)
        return retval

class GrokClient(object):
    def __new__(cls, *args,**kwargs):
        print("loading subgrokclient")
        try:
           retval = object.__new__(GrokClientInner,*args,**kwargs)
        except:
           from .client_groq import GrokClient as GrokClientInner
           retval = object.__new__(GrokClientInner,*args,**kwargs)
        retval.__init__(*args,**kwargs)
        return retval

class OpenAIClientWrapper(object):
    def __new__(cls, *args,**kwargs):
        print("loading openai compatible client")
        try:
           retval = object.__new__(OpenAIClient,*args,**kwargs)
        except:
           from .client_openai import OpenAIClient
           retval = object.__new__(OpenAIClient,*args,**kwargs)
        retval.__init__(*args,**kwargs)
        return retval

class DummyClient:

    def send_prompt(self,p,params=None,callback=None):
        print(p.messages)
        return ["{ \"answer\": \"dummy response\"}"]

    def connect(self):
        pass

    def get_model_name(self):
        return ""

class LLamaCppClient:
    def __init__(self,host=DEFAULT_HOST, port=80800):
        self.host = host
        self.port = port
        self.client_parameters = {}
        a = {}
        a["n_predict"] = 1024*1
        a["stop"] = ["<|eom_id|>","<|eot_id|>","<|end|>", "<|im_end|>", "</s>","<end_of_turn>","<|im_start|>","[|endofturn|]"]
        #        a["temperature"] = 0.0
        a["seed"] = -1
        a["cache_prompt"] = True
        a["stream"] = True
        # a["n_probs"] = 10
        # a["n_keep"] = -1
        # a["top_k"] = 5
        self.prompt_metadata= {}
        self.default_params = a
        self.connected = False

    def get_formatter_config(self):
        props = self.get_server_props()
        model_props = {"model_name": self.model_name}
        if "chat_template" in props:
            model_props["chat_template"] = props["chat_template"]
            if "bos_token" in props:
                model_props["bos_token"] = props["bos_token"]
        return model_props

    def connect(self):
        if not self.connected:
            props = self.get_server_props()
            self.max_slots = props.get("total_slots",1)

            if "model_path" in props:
                model_path = props["model_path"]
            else:
                model_path = props["default_generation_settings"]["model"]
            model_name = model_path.split("/")[-1]
            self.model_name = model_name
            self.formatter = Formatter()
            model_props = self.get_formatter_config()


            self.formatter.load_model(model_props)
            #get_formatter(props)
            self.connetion_semaphore = BoundedSemaphore(value = self.max_slots)
            self.connected = True

    def set_parameters(self,parameters):
        client_config_names=["host","port"]
        if "port" in parameters:
            self.port = parameters["port"]
        if "host" in parameters:
            self.host = parameters["host"]
            self.connect()
        else:
            self.parameters = parameters

    def get_model_name(self):
        return self.model_name

    def get_server_props(self):
        if self.connected:
            return self.server_props
        url = "http://" + self.host + ":" + str(self.port) + "/props"

        retries = 10
        while retries > 0:
            r = requests.get(url)
            resp = json.loads(r.content)
            retries -= 1
            if "error" in resp:
                print("server busy")
                time.sleep(2)
            else:
                break
        max_context = resp["default_generation_settings"]["n_ctx"]

        # try detecting the bos token
        if "chat_template" in resp:
            try:
                rendered = self.tokenize("<<<<USER>>>>", add_special=True,with_pieces=True)
                textval = "".join([el["piece"] for el in rendered])
                bos_token = textval[:textval.find("<<<<USER>>>>")]
                resp["bos_token"] = bos_token
            except:
                pass
       
        self.context_size = max_context
        self.server_props = resp
        return resp

    def _ricevi(self,req_params, pass_raw,callback):
        ret = []
        with self.connetion_semaphore:
          with requests.post(**req_params) as r1:
            a = 1
            for line in r1.iter_lines():
                # filter out keep-alive new lines
                a = a + 1
                if line:
                    decoded_line = line.decode('utf-8')
                    json_decoded = json.loads(decoded_line[6:])
                    if ("stop" not in json_decoded) or json_decoded["stop"]:
                        self.prompt_metadata = json_decoded

                    if "truncated" in json_decoded and (json_decoded["truncated"] or False):
                        del json_decoded["prompt"]
                        print(json.dumps(json_decoded,indent=4))

                        raise Exception("truncated")
                    if "content" not in json_decoded:
                        print(json_decoded)


                    if pass_raw and len(json_decoded["content"]) > 0:
                        tmp_res = json_decoded['completion_probabilities']
                        #print(tmp_res)
                        if len(tmp_res) == 0:
                            continue
                        tmp_res = tmp_res[0]["probs"]
                        tmp_res = [ (el["tok_str"],el["prob"]) for el in tmp_res ]
                        tmp_res = str(tmp_res) + "\n"
                        #
                    else:
                        tmp_res =json_decoded["content"]
                    if callback:
                        callback(tmp_res)
                    if len(tmp_res) > 0:
                        ret.append(tmp_res)
                    
        if self.prompt_metadata.get("stopped_eos",False):
            eos_tokens = ["<|endoftext|>"]
            if len(ret) > 0 and ret[-1] in eos_tokens:
                ret = ret[:-1]
        retstring = "".join(ret)
        return retstring

    def tokenize(self,p,add_special=False, with_pieces=False):
        url = "http://" + self.host + ":" + str(self.port) + "/tokenize"
        a={}
        a["content"] = p
        a["add_special"] = add_special
        if with_pieces:
            a["with_pieces"] = with_pieces
        js = json.dumps(a)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url,data=js,headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        r4 = r3["tokens"]
        #print("tokens: ", len(r4))
        return r4
    
    def detokenize(self,p):
        url = "http://" + self.host + ":" + str(self.port) + "/detokenize"
        a={}
        a["tokens"] = p
        js = json.dumps(a)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url,data=js,headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        #print(r3)
        return r3

    def _set_prompt_legacy(self,obj, prompt,tokens):

        obj["prompt"] = tokens

    def _send_prompt_text(self, p, params,callback):
        tokens = self.tokenize(p)
        #detokenized = self.detokenize(tokens)

        a = merge_params(self.default_params,params)
        self._set_prompt_legacy(a,p,tokens)
        #a["prompt"] = p

        if len(tokens) +a["n_predict"] >= self.context_size:
            raise Exception("context size exceeded: " + str(len(tokens)) + " + " + str(a["n_predict"]))

        #a = {"messages":p}
        js = json.dumps(a)
        #print(a,"\n-\n" + p + "-")
        url = "http://" + self.host + ":" + str(self.port) +"/completion"
        headers = {"Content-Type": "application/json"}

        data = js
        pass_raw = "n_probs" in a

        req_params = {"url":url,"data":data,"headers":headers,"stream":True}
        g = self._ricevi(req_params,pass_raw,callback)
        return g

    def _send_prompt_builder(self,p,params,callback):
        prompt = p._build()
        return self._send_prompt_text(prompt,params,callback)

    def apply_format_templates(self,prompt):
        return self.formatter.apply_format_templates(prompt)

    def send_prompt(self,p,params=None,callback=None):
        if params is None:
            params = self.client_parameters
        if isinstance(p,str):
            return self._send_prompt_text(p,params,callback)
        else:
            return self._send_prompt_builder(p,params,callback)

class Client:

    client_configs = None
    @staticmethod
    def get_client(client_name):
        
        client_config = Client.client_configs[client_name]
        client =  Client._make_client_simple(client_name,client_config)
        client.connect()
        return client

    @staticmethod
    def _make_client_simple(client_name, client_config):
        if "type" in client_config:
            del client_config["type"]
        if client_name=="dummy":
            return DummyClient()
        elif client_name == "llama_cpp":
            conf = client_config
            return LLamaCppClient(**conf)
        elif client_name == "groq":
            conf = client_config
            return GrokClient(**conf)
        elif client_name.lower() == "openai":
            conf = client_config
            return OpenAIClientWrapper(**conf)

    @staticmethod
    def _make_client_list(client_names, client_configs):
        for client_name in client_names:
            client_config = client_configs.get(client_name,{})
            type = client_config.get("type",client_name)
            if "type" in client_config:
                del client_config["type"]
            try:
               client = Client._make_client_simple(type,client_config)
               client.connect()
               return client
            except Exception as e:
               last_exc = e
        raise last_exc from None


    @staticmethod
    def make_client(client_config):
        Client.client_configs = client_config
        client_name = client_config.get("client_name","dummy")
        if isinstance(client_name,list):
            return Client._make_client_list(client_name, client_config)
        else:
            client_config = client_config.get(client_name,{})
            return Client._make_client_simple(client_name,client_config)
