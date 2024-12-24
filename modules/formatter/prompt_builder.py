from .parser import parse_raw, check_special_tokens
from transformers import AutoTokenizer
from .formatter_hf import FormatterHF
from .formatter_custom import FormatterCustom

import copy

class Formatter:
    def __init__(self):
        self.formatter = None
        self.model_name = None

    def load_model(self,model_name):
        self.model_name = model_name
        self.formatter = FormatterHF()
        if self.formatter.load_model(model_name):
            return True
        self.formatter = FormatterCustom()
        self.formatter.load_model(model_name)
        return True

    def build_prompt(self,messages,force_system=False):
        messages = copy.deepcopy(messages)
        
        prompt = self.formatter.build_prompt(messages,force_system)
        #workaround per deepseek
        if self.model_name.lower().startswith("deepseek") and prompt.endswith("Assistant: "):
            prompt = prompt[:-1]
            # workaround per deepseek
        if self.model_name.lower().startswith("glm") and prompt.endswith("<|assistant|>\n"):
            prompt = prompt[:-1]


        return prompt


## questa è la parte che non ha bisongno di conoscere il modello

class PromptBuilder:
    def __init__(self):
        self.formatter = Formatter()
        self.sysprompt = "You are a helpful assistant"
        self.force_system=False
        self.messages = []
        self.reset()

    @staticmethod
    def _check_special_tokens(m):
        is_raw = check_special_tokens(m)
        return is_raw

    def set_param(self,name,val):
        if name == "force_system":
             self.force_system = val
        elif name == "sysprompt":
             self.sysprompt = val
             self.reset()

    def _build(self):
        text_prompt = self.formatter.build_prompt(self.messages,force_system=self.force_system)
#        print(text_prompt)
        return text_prompt

    def __str__(self):
        decorated_messages = ["{p:" + el["role"] + "}\n" + el["content"] + "{p:eom}" for el in self.messages]
        text_prompt = "{p:bos}\n\n" + "\n\n".join(decorated_messages)
        return text_prompt


    def load_model(self,model_name):
        self.formatter.load_model(model_name)

    def reset(self):
        self.messages = []
        self.messages.append({"role":"system","content":self.sysprompt})
        self.first_prompt = True

    def set_from_raw(self,message):
        self.messages = parse_raw(message)

    def add_request(self, message,role="user"):
        m = message
        is_raw = self._check_special_tokens(m)

        if is_raw:
            try:
                parsed = parse_raw(message)
            except:
                parsed = [{"role":"raw","content":str(m)}]
        else:
            parsed = [{"role":role,"content":str(m)}]

        for el in parsed:
            if el["role"] == "raw":
                self.messages = [el]
            elif el["role"] == "system":
                if self.messages[0]["role"] == "system":
                    self.messages[0] = el
            else:
                self.messages.append(el)

        return self.messages

    def add_response(self,message,role = "assistant"):
        if(self.messages[-1]["role"] == "assistant"):
            self.messages[-1]["content"] = self.messages[-1]["content"]  + str(message)
        else:
            self.messages.append({"role":role,"content":str(message)})
        return self.messages
        



if __name__ == "__main__":
    a = PromptBuilder()
    f = open("test/raw.txt","r")
    message = f.read()
    f.close()
    a.set_from_raw(message)
