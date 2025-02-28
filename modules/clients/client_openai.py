from openai import OpenAI
import copy
import requests
import json

class OpenAIClient():

    def __init__(self, dummy=None, **extra_client_args):
        print("openai init")

        self.model_name = "llama3-70b-8192"
        self.extra_client_args = {}
        for el in ["api_key","base_url"]:
            if el in extra_client_args:
                self.extra_client_args[el] = extra_client_args[el]
        
        for el in ["model","model_name"]:
            if el in extra_client_args:
                self.model_name =  extra_client_args[el]

        self.client = None
        self.prompt_metadata = {}
        
        self.default_params = {"temperature": 0.1, "max_tokens": 1024 // 2, "stream": True, "stop": None}

    def tokenize(self, p):
        request_body = {
            "model": self.model_name,
            "add_special_tokens": True,
            "add_generation_prompt": False,
        }
        if isinstance(p,list):
            request_body["messages"] = p
        else:
            request_body["prompt"] = p
        url = str(self.client.base_url)[:-4]+ "/tokenize"
        headers = {"Content-Type": "application/json","accept": "application/json"}
        r = requests.post(url, data=json.dumps(request_body), headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        r4 = r3["tokens"]
        # print("tokens: ", len(r4))
        return r4

    def detokenize(self, tokens):
        request_body = {
            "model": self.model_name,
            "tokens": tokens,
        }

        url = str(self.client.base_url)[:-4]+ "/detokenize"
        headers = {"Content-Type": "application/json","accept": "application/json"}
        r = requests.post(url, data=json.dumps(request_body), headers=headers)
        r1 = r.text
        r2 = r1
        r3 = json.loads(r2)
        r4 = r3["prompt"]
        # print("tokens: ", len(r4))
        return r4

    def send_prompt(self, p, params=None, callback=None):
        if isinstance(p, list):
            messages = p
        else:
            messages = p.get_messages()
        # print(messages)
        #self.detokenize(self.tokenize(messages))
        user_params = params
        params = copy.deepcopy(self.default_params)
        if user_params:
            params["stop"] = user_params.get("stop", params["stop"])
            params["temperature"] = user_params.get("temperature", params["temperature"])
            params["max_tokens"] = user_params.get("n_predict", params["max_tokens"])
        if "max_tokens" in params and params["max_tokens"] <= 0:
            del params["max_tokens"]
        model_name = self.model_name
        if messages[-1].get("role","") == "assistant":
            extra_body = {}
            extra_body["add_generation_prompt"] = False
            extra_body["continue_final_message"] = True
            params["extra_body"] = extra_body

        completion = self.client.chat.completions.create(model=self.model_name, messages=messages, **params)
        return self.ricevi(completion, callback)

    def ricevi(self, completion, callback=None):
        res = ""
        for chunk in completion:

            val = chunk.choices[0].delta.content or ""
            res += val
            if callback:
                callback(val)
        return res

    def connect(self):
        if not self.client:
            self.client = OpenAI(**self.extra_client_args)

    def get_model_name(self):
        return "grok"

if __name__ == "__main__":
     client = OpenAIClient()
     client.connect()
     messages=[ { "role": "user", "content": "Hello, tell me your name" }]
     params={ "temperature":1, "max_tokens":1024, "top_p":1, "stream":True, "stop":None}
     result = client.send_prompt(messages,params)
     for el in result:
         print(el,end="")
     print("")
