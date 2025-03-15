from groq import Groq
import copy

class GrokClient():

    def __init__(self,dummy=None,api_key=""):
        print("grokclient init")
        self.api_key=api_key
        self.client = None
        self.prompt_metadata={}
        self.model_name="deepseek-r1-distill-llama-70b"
        self.default_params={ "temperature":0.1, "max_tokens":1024*4, "stream":True, "stop":None}

    def send_prompt(self,p,params=None, callback=None):
        if isinstance(p,list):
            messages = p
        else:
            messages = p.get_messages()
        #print(messages)
        user_params = params
        params = copy.deepcopy(self.default_params)
        if user_params:
            params["stop"] = user_params.get("stop",params["stop"])
            params["temperature"] = user_params.get("temperature",params["temperature"])
            params["max_tokens"] = user_params.get("n_predict",params["max_tokens"])
        if "max_tokens" in params and params["max_tokens"] <= 0:
            del params["max_tokens"]
        model_name = self.model_name
        completion = self.client.chat.completions.create( model=self.model_name, messages=messages,**params)
        return self.ricevi(completion,callback)

    def ricevi(self,completion,callback=None):
        res = ""
        for chunk in completion:
             
             val = chunk.choices[0].delta.content or ""
             res += val
             if callback:
                callback(val)
        return res

    def connect(self):
        if not self.client:
            self.client = Groq(api_key=self.api_key)

    def get_model_name(self):
        return "grok"



if __name__ == "__main__":
     client = GrokClient()
     client.connect()
     messages=[ { "role": "user", "content": "Hello, tell me your name" }]
     params={ "temperature":1, "max_tokens":1024, "top_p":1, "stream":True, "stop":None}
     result = client.send_prompt(messages,params)
     for el in result:
         print(el,end="")
     print("")

