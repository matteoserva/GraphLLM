import onnxruntime_genai as og
import argparse
import time
from transformers import AutoModelForCausalLM, AutoTokenizer


class ONNXClient():

    def __init__(self,dummy=None):
        print("GLM client init")
        self.client = None
        self.model_name="Phi-3-small"
        self.default_params = {}


    def send_prompt(self,p,params=None):


        if isinstance(p,list):
            if isinstance(p,list):
                messages = p
            else:
                messages = p.get_messages()
            print(messages)

            input_string = self.tokenizer.apply_chat_template(messages,add_special_tokens=True, add_generation_prompt=True,tokenize=False)
            print(input_string)
        elif isinstance(p,str):
            input_string = p
        else:
            input_string = p._build()
        #input_string = input_string.replace("<s>","",1)
        model_inputs = self.tokenizer.encode(input_string)

        gparams = og.GeneratorParams(self.model)

        args = self.default_params
        search_options = {name:getattr(args, name) for name in ['do_sample', 'max_length', 'min_length', 'top_p', 'top_k', 'temperature', 'repetition_penalty'] if name in args}
        #if "n_predict" in params:
        #    search_options["max_length"] = len(model_inputs) + params["n_predict"]
        if "temperature" in params:
            search_options["temperature"] = params["temperature"]
        if "top_k" in params:
            search_options["top_k"] = params["top_k"]
        #if "repeat_penalty" in params:
        #    search_options["repetition_penalty"] = params["repeat_penalty"]
        if 'max_length' not in search_options:
            search_options['max_length'] = 2048
        gparams.set_search_options(**search_options)
        gparams.input_ids = model_inputs

        res = self.ricevi(self.model,gparams)
        return res



    def ricevi(self,model,generate_kwargs):
        received = ""
        generator = og.Generator(model, generate_kwargs)
        while not generator.is_done():
                generator.compute_logits()
                generator.generate_next_token()

                new_token = generator.get_next_tokens()[0]
                val = self.tokenizer_stream.decode(new_token)
                yield val
                received += val
                if "Observation:" in received:
                    break
        del generator

    def connect(self):

        self.model = og.Model("/home/matteo/tmp/models_cache/Phi-3-small-8k-instruct-onnx-cuda/cuda-int4-rtn-block-32")
        self.tokenizero = og.Tokenizer(self.model)
        self.tokenizer = AutoTokenizer.from_pretrained("/home/matteo/tmp/models_cache/Phi-3-small-8k-instruct", trust_remote_code=True)
        self.tokenizer_stream = self.tokenizero.create_stream()
        
    def get_model_name(self):
        return self.model_name

if __name__ == "__main__":
    client = ONNXClient("Phi")
    client.connect()
    model = client.model
    tokenizer = client.tokenizer
    streamer = client.streamer

    r = client.send_prompt("Hello")

    for new_token in r:
        print(new_token, end="", flush=True)

