from modules.formatter import PromptBuilder
import json
import requests
#from . import common
from ..common import get_formatter,build_prompt,merge_params
from ..formatter import Formatter
import time
import copy
from threading import BoundedSemaphore
from .client_llamacpp import LLamaCppClient



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



class ClientWrapper:
    def __init__(self,client_name=None):
        self.clients_cache = {}
        if client_name:
            client = ClientFactory._get_client_internal(client_name)
        else:
            client = ClientFactory.make_client_default()
        self.client = client
    
    def __getattr__(self, name):
        try:
            attr = getattr(self.client, name)
        except AttributeError:
            raise

        if not callable(attr):
            return attr
            
        def method_proxy(*args,**kwargs):
            return self.call_client_method(name,*args,**kwargs)
        
        return method_proxy
        
    def call_client_method(self, method_name,*args,**kwargs):
        attr = getattr(self.client, method_name)
        return attr(*args,**kwargs)

class ClientFactory:

    client_configs = None
    backends = []
    
    @staticmethod
    def _get_client_internal(client_name):
        if ":" in client_name:
            client_name, model= client_name.split(":",1)
            client_config = ClientFactory.client_configs[client_name]
            client_config = {el: client_config[el] for el in client_config}
            client_config["model"] = model
        else:
            client_config = ClientFactory.client_configs[client_name]
        client =  ClientFactory._make_client_simple(client_config["type"],client_config)
        client.connect()
        return client

    def get_client(client_name=None):
        return ClientWrapper(client_name)

    @staticmethod
    def _make_client_simple(client_name, cfg):
        client_config = cfg.copy()
        if "type" in client_config:
            del client_config["type"]
        if client_name=="dummy":
            return DummyClient()
        elif client_name == "llama_cpp" or client_name == "llama_swap":
            conf = client_config
            return LLamaCppClient(**conf)
        elif client_name == "groq":
            conf = client_config
            return GrokClient(**conf)
        elif client_name.lower() == "openai":
            conf = client_config
            return OpenAIClientWrapper(**conf)

    @staticmethod
    def _make_client_list(client_names):
        client_configs = ClientFactory.client_configs
        for client_name in client_names:
            client_config = client_configs.get(client_name,{})
            client_type = client_config.get("type",client_name)
            try:
               client = ClientFactory._make_client_simple(client_type,client_config)
               client.connect()
               return client
            except Exception as e:
               last_exc = e
        raise last_exc from None


    @staticmethod
    def make_client_default():
        return ClientFactory._make_client_list(ClientFactory.backends)

            
    @staticmethod
    def load_config(client_config):
        ClientFactory.client_configs = client_config
        backends = client_config.get("client_name","dummy")
        if not isinstance(backends,list):
            backends = [backends]
        if len(backends) < 1:
            backends = ["dummy"]
        ClientFactory.backends = backends
        


