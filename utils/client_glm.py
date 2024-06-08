import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    StoppingCriteria,
    StopStringCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer
)
from threading import Thread

class StopOnTokens(StoppingCriteria):
    def __init__(self,model):
        self.model = model
        
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = self.model.config.eos_token_id
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False

class GLMClient():

    def __init__(self,dummy=None):
        print("GLM client init")
        self.client = None
        if dummy == "Phi":
            self.model_name="Phi-3-small"
            self.model_path="/home/matteo/tmp/models_cache/Phi-3-small-8k-instruct"
        else:
            self.model_name="GLM-4"
            self.model_path="/home/matteo/tmp/models_cache/glm-4-9b-chat"
        self.default_params = {}


    def send_prompt(self,p,params=None):


        if isinstance(p,list):
            if isinstance(p,list):
                messages = p
            else:
                messages = p.messages
            print(messages)
            params = self.default_params
            model_name = self.model_name

            input_string = self.tokenizer.apply_chat_template(messages,add_special_tokens=True, add_generation_prompt=True,tokenize=False)
            print(input_string)
        elif isinstance(p,str):
            input_string = p
        else:
            input_string = p._build()

        model_inputs = self.tokenizer(input_string,add_special_tokens=False,return_tensors="pt")["input_ids"].to(self.model.device)
        #print(model_inputs)
        #model_in_native = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True,tokenize=True,return_tensors="pt").to(self.model.device)
        #print(model_in_native)
        
        stops = StopStringCriteria(self.tokenizer,["Observation:"])
        generate_kwargs = {
                    "input_ids": model_inputs,
                    "streamer": self.streamer,
                    "max_new_tokens": 1024,
                    "do_sample": True,
                    "top_p": 0.8,
                    "min_p": 0.1,
                    "temperature": 0.6,
                    #"stopping_criteria": StoppingCriteriaList([self.stop,stops]),
                    "stopping_criteria": StoppingCriteriaList([stops]),
                    "repetition_penalty": 1.0,
                    #"output_scores": True, "return_dict_in_generate":True,
                    #"num_beams": 5,
                    "eos_token_id": self.model.config.eos_token_id,
                }
        if "n_predict" in params:
            generate_kwargs["max_new_tokens"] = params["n_predict"]
        if "temperature" in params:
            generate_kwargs["temperature"] = params["temperature"]
        if "top_k" in params:
            generate_kwargs["top_k"] = params["top_k"]
        if "repeat_penalty" in params:
            generate_kwargs["repetition_penalty"] = params["repeat_penalty"]


        res = self.ricevi(self.model,generate_kwargs)
        return res

    def ricevi2(self,model,generate_kwargs):
        res = model.generate(**generate_kwargs)
        res2 = self.tokenizer.decode(res.sequences[0], skip_special_tokens=True)
        return res2

    def ricevi(self,model,generate_kwargs):
        t = Thread(target=model.generate, kwargs=generate_kwargs)
        t.start()
        for new_token in self.streamer:
                    if new_token:
                        yield new_token
        t.join()

    def connect(self):
        device = "cuda"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path,low_cpu_mem_usage=True,trust_remote_code=True,
            #load_in_4bit=True
            load_in_8bit=True
            ).eval()
        self.streamer = TextIteratorStreamer(tokenizer=self.tokenizer,timeout=60,skip_prompt=True,skip_special_tokens=True)
        self.stop = StopOnTokens(self.model)
        
    def get_model_name(self):
        return self.model_name

if __name__ == "__main__":
    client = GLMClient("Phi")
    client.connect()
    model = client.model
    tokenizer = client.tokenizer
    streamer = client.streamer

    messages = [
        {"role": "user", "content": "S is the sum of the first 10 even natural numbers. output the square of S. Then output the cube of S"},
    ]
    # 

    r = client.send_prompt(messages)


    for new_token in r:
        print(new_token, end="", flush=True)
