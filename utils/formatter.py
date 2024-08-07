from .parser import parse_raw, check_special_tokens
from transformers import AutoTokenizer
import copy

class Formatter:
    def __init__(self):
        self.hf_formatter = None

    def load_hf_model(self,model_name):
        self.model_name = model_name
        model_name = model_name.lower()
        if model_name.lower().startswith("phi-3-small"):
            tokenizer_path = "tokenizers/phi3-small"
        elif model_name.lower().startswith("_phi"):
            tokenizer_path = "tokenizers/phi3-mini"
        elif model_name.lower().find("_llama-3.1") >= 0:
            tokenizer_path = "/home/matteo/tmp/models_cache/Meta-Llama-3.1-8B-Instruct"
        elif model_name.lower().startswith("_glm"):
            tokenizer_path = "tokenizers/glm-chat"
        elif model_name.lower().startswith("_mistral-nemo"):
            tokenizer_path = "tokenizers/mistral-nemo"
        elif model_name.lower().startswith("_codegeex"):
            tokenizer_path = "/home/matteo/tmp/models_cache/codegeex4-all-9b"
        elif model_name.lower().startswith("qwen2"):
            tokenizer_path = "tokenizers/Qwen2"
        elif model_name.lower().startswith("_gemma"):
            tokenizer_path = "tokenizers/gemma-2-27b-it"
        elif model_name.lower().startswith("_deepseek"):
            tokenizer_path = "tokenizers/DeepSeek-V2-Lite-Chat"
        else:
            return None
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
        self.tokenizer = tokenizer
        return tokenizer

    def load_custom_model(self,model_name):
#        print("Model name:",model_name)
        self.model_name = model_name
        formatter={}
        formatter["enable_system"] = True
        if model_name.find("c4ai-command-r") >= 0:
            formatter={}
            formatter["bos"]=""
            formatter["bor"]="<|START_OF_TURN_TOKEN|><|"
            formatter["eor"]="_TOKEN|>"

            formatter["eom"]="<|END_OF_TURN_TOKEN|>"

            formatter["system_name"]="SYSTEM"
            formatter["user_name"]="USER"
            formatter["assistant_name"]="CHATBOT"


            formatter["enable_system"] = False
            formatter["roles"] = ["raw","user","assistant"]
        elif model_name.lower().find("glm") >= 0 or model_name.lower().find("codegeex") >= 0:
            formatter={}
            formatter["bos"]="[gMASK]<sop>"
            formatter["bor"]="<|"
            formatter["eor"]="|>\n"

            formatter["eom"]=""

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"


            formatter["enable_system"] = False
            formatter["roles"] = ["raw","user","assistant","system"]
        elif model_name.lower().find("yuan") >= 0:
            formatter={}
            formatter["bos"]=""
            formatter["bos"]=""
            formatter["bor"]=""
            formatter["eor"]=""

            formatter["eom"]="\n"

            formatter["system_name"]=""
            formatter["user_name"]="Instruction: "
            formatter["assistant_name"]="Response:\n"
            formatter["role_string"] = {"user":"","assistant":"","system":""}
            formatter["role_eom"] = {"user":"<sep>","assistant":"<n>","system":"\n"}
            formatter["enable_system"] = False
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().find("platypus-yi") >= 0:
            formatter={}
            formatter["bos"]=""
            formatter["bos"]=""
            formatter["bor"]=""
            formatter["eor"]=""

            formatter["eom"]="\n"

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            formatter["role_string"] = {"user":"USER: ","assistant":"ASSISTANT: ","system":""}
            formatter["role_eom"] = {"user":"\n","assistant":"\n","system":"\n"} 

            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().find("deepseek") >= 0:
            formatter={}
            formatter["bos"]="<｜begin▁of▁sentence｜>"
            formatter["bor"]=""
            formatter["eor"]=""

            formatter["eom"]="\n"

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            formatter["role_string"] = {"user":"User: ","assistant":"Assistant: ","system":""}
            formatter["role_eom"] = {"user":"\n\n","assistant":"<｜end▁of▁sentence｜>","system":"\n\n"} 

            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().startswith("internlm"):
            formatter={}
            formatter["bos"]="<s>"
            formatter["bor"]="<|im_start|>"
            formatter["eor"]="\n"

            formatter["eom"]="<|im_end|>\n"

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            #formatter["role_string"] = {"user":"<|im_start|>user\n","assistant":"<|im_start|>assistant\n","system":""}
            #formatter["role_eom"] = {"user":"<|im_end|>\n","assistant":"<|im_end|>\n","system":""} 

            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().startswith("yi") or model_name.lower().startswith("faro") or model_name.lower().startswith("orca"):
            formatter={}
            formatter["bos"]="<|startoftext|>"
            formatter["bos"]=""
            formatter["bor"]="<|im_start|>"
            formatter["eor"]="\n"

            formatter["eom"]="<|im_end|>\n"

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            #formatter["role_string"] = {"user":"<|im_start|>user\n","assistant":"<|im_start|>assistant\n","system":""}
            #formatter["role_eom"] = {"user":"<|im_end|>\n","assistant":"<|im_end|>\n","system":""} 

            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().startswith("calme"):
            formatter={}
            formatter["bos"]="<|startoftext|>"
            formatter["bos"]=""
            formatter["bor"]="<|im_start|>"
            formatter["eor"]="\n"

            formatter["eom"]="<|im_end|>\n"

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            formatter["role_string"] = {"user":"<|im_start|>user\n","assistant":"<|im_start|>assistant\n","system":""}
            formatter["role_eom"] = {"user":"<|im_end|>\n","assistant":"<|im_end|>\n","system":"<|im_end|>\n"}

            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().startswith("wizardlm"):
            formatter={}
            formatter["bos"]=""
            formatter["bos"]=""
            formatter["bor"]=""
            formatter["eor"]=""

            formatter["eom"]="\n"

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            formatter["role_string"] = {"user":"USER: ","assistant":"ASSISTANT: ","system":""}
            formatter["role_eom"] = {"user":" ","assistant":"</s>","system":" "} 

            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
        elif model_name.lower().startswith("mistral-nemo"):
            formatter={}
            formatter["bos"]="<s>"
            formatter["bor"]=""
            formatter["eor"]=""

            formatter["eom"]=""

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            formatter["role_string"] = {"user":"[INST] ","assistant":"","system":"[INST]"}
            formatter["role_eom"] = {"user":"[/INST]","assistant":"","system":"[/INST]"} 

            formatter["enable_system"] = False
            formatter["roles"] = ["raw","user","assistant"]
        elif model_name.lower().startswith("mistral") or model_name.lower().startswith("mixtral"):
            formatter={}
            formatter["bos"]=""
            formatter["bor"]=""
            formatter["eor"]=""

            formatter["eom"]=""

            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            formatter["role_string"] = {"user":"[INST]_","assistant":"","system":"[INST]"}
            formatter["role_eom"] = {"user":"[/INST]","assistant":"","system":"[/INST]"} 

            formatter["enable_system"] = False
            formatter["roles"] = ["raw","user","assistant"]
        elif model_name.lower().startswith("gemma"):
            formatter={}
            formatter["bos"]="<bos>"
            formatter["bor"]="<start_of_turn>"
            formatter["eor"]="\n"

            formatter["eom"]="""<end_of_turn>\n"""
            formatter["system_name"]="user"
            formatter["user_name"]="user"
            formatter["assistant_name"]="model"

            formatter["enable_system"] = False
            formatter["roles"] = ["raw","user","assistant"]
        elif ( (model_name.lower().startswith("phi") and model_name.find("updated") >= 0) or
              model_name.lower().startswith("phi-3.1") ):
            formatter={}
            formatter["bos"]="<s>"
            if model_name.lower().find("medium") >= 0:
                formatter["bos"]="<s>"
            formatter["bor"]="<|"
            formatter["eor"]="|>\n"
            formatter["lf"] = "<0x0A>"
            formatter["eom"]="""<|end|>\n"""
            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"
            print("phi 3 updated")
            formatter["enable_system"] = True
            formatter["roles"] = ["raw","system","user","assistant"]
            formatter["role_eom"] = {"user":"<|end|>\n","assistant":"<|end|>\n","system":"<|end|>\n"}
        elif model_name.lower().startswith("phi"):
            formatter={}
            formatter["bos"]="<s>"
            if model_name.lower().find("medium") >= 0:
                formatter["bos"]="<s>"
            formatter["bor"]="<|"
            formatter["eor"]="|>\n"
            formatter["lf"] = "<0x0A>"
            formatter["eom"]="""<|end|>\n"""
            formatter["system_name"]="user"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"

            formatter["enable_system"] = False
            formatter["roles"] = ["raw","user","assistant"]
            formatter["role_eom"] = {"user":"<|end|>\n","assistant":"<|end|>\n","system":"\n\n"}
        elif model_name.lower().startswith("openchat"):
            formatter["bos"] = "<|begin_of_text|>"  ##non capisco
            # formatter["bos"]=""
            formatter["bor"] = "<|start_header_id|>"
            formatter["eor"] = "<|end_header_id|>\n\n"

            formatter["eom"] = """<|eot_id|>"""
            # formatter["row"]=formatter["row1"] + formatter["row2"]
            formatter["roles"] = ["raw", "system", "user", "assistant"]
            formatter["system_name"] = "System"
            formatter["user_name"] = "GPT4 Correct User"
            formatter["assistant_name"] = "GPT4 Correct Assistant"
        else: #llama

            formatter["bos"]="<|begin_of_text|>" ##non capisco
            #formatter["bos"]=""
            formatter["bor"]="<|start_header_id|>"
            formatter["eor"]="<|end_header_id|>\n\n"

            formatter["eom"]="""<|eot_id|>"""
            #formatter["row"]=formatter["row1"] + formatter["row2"]
            formatter["roles"] = ["raw","system", "user","assistant","ipython","call"]
            formatter["role_string"] = {"call":"<|start_header_id|>assistant<|end_header_id|>\n\n"}
            formatter["role_eom"] = {"call":"<|eom_id|>"}
            formatter["system_name"]="system"
            formatter["user_name"]="user"
            formatter["assistant_name"]="assistant"

        return formatter

    def load_model(self,model_name):
        self.hf_formatter = self.load_hf_model(model_name)
        self.f = self.load_custom_model(model_name)

    def build_hf_prompt(self,messages,force_system=False):
        # se il primo è raw, allora salva così com'è
        #     se il secondo è presente e assistant, appendi senza preamble?
        # se l'ultimo è raw o assistant allora non mettere il generation token
        # se l'ultimo è raw o assistant non mettere eom
        # se il primo è system e manca il system, allora attaccalo al primo
        
        has_system = True
        try:
            has_system = self.tokenizer.chat_template.find("system") >= 0
        except:
            pass

        if messages[0]["role"] == "system" and not has_system:
            messages[0]["role"] = "user"
            if len(messages) > 1:
                messages[1]["content"] = messages[0]["content"]+"\n\n" + messages[1]["content"]
                messages = messages[1:]

        assistant_prompt = None
        if messages[-1]["role"] == "assistant":
            assistant_prompt = messages[-1]["content"]
            messages = messages[:-1]

        raw_prompt = None
        if messages[0]["role"] == "raw":
            a = messages[0]["content"]
            a = a.replace("{p:bos}\n", self.tokenizer.bos_token)
            a = a.replace("{p:bos}", self.tokenizer.bos_token)
            raw_prompt = a
            #messages = messages[1:]

        if raw_prompt is None:
            input_string = self.tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)
        else:
            if len(messages) == 1:
                input_string = raw_prompt
            else:
                assistant_response = messages[1]["content"]
                placeholder_string="<<<<|>>>>PLACEHOLDER<<<|>>>"
                messages[0]["role"] ="user"
                messages[0]["content"]="AAAA"
                messages[1]["content"]=placeholder_string
                input_string = self.tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)

                el = input_string.find(placeholder_string)+len(placeholder_string)
                input_string = raw_prompt + assistant_response+input_string[el:]

        #workaround
        #if hasattr(self.hf_formatter,"name") and self.hf_formatter.name.lower().startswith("glm4") and input_string.endswith("<|assistant|>"):
        #    input_string += "\n"

        #if hasattr(self.hf_formatter,"name") and self.hf_formatter.name.lower().startswith("glm4") and input_string.endswith("<|assistant|>"):
        #    input_string += "\n"

        if assistant_prompt is not None:
            input_string = input_string + assistant_prompt

        return input_string

    def apply_format_templates(self, prompt):
        formatter = self.f
        a = prompt
        system_name = "system"
        if not formatter["enable_system"]:
            system_name = "user"
        a = a.replace("{p:bos}\n",formatter["bos"])
        a = a.replace("{p:bos}",formatter["bos"])
        a = a.replace("\n{p:system}\n",formatter["bor"]+formatter["system_name"]+formatter["eor"])
        a = a.replace("{p:eom}\n",formatter["eom"])
        a = a.replace("\n{p:user}\n",formatter["bor"]+formatter["user_name"]+formatter["eor"])
        a = a.replace("\n{p:assistant}\n",formatter["bor"]+formatter["assistant_name"]+formatter["eor"])
        return a
    
    def build_prompt(self,messages,force_system=False):
        messages = copy.deepcopy(messages)
        
        if self.hf_formatter is not None:
            prompt = self.build_hf_prompt(messages,force_system)
        else:
            prompt = self.build_handmade_prompt(messages,force_system)
        
        #workaround per deepseek
        if self.model_name.lower().startswith("deepseek") and prompt.endswith("Assistant: "):
            prompt = prompt[:-1]
            # workaround per deepseek
        if self.model_name.lower().startswith("glm") and prompt.endswith("<|assistant|>\n"):
            prompt = prompt[:-1]


        return prompt

    def build_handmade_prompt(self,messages,force_system=False):
    
        formatter = self.f
        skip_bos = False
        skip_final = False
        modifiers = [ {"skip_preamble":False,"skip_postamble":False} for el in messages]
        fake_system = False

        if messages[0]["role"] == "raw":
            skip_bos = True
            if len(messages) > 1 and messages[1]["role"] == "assistant":
                modifiers[1]["skip_preamble"] = True
        if messages[-1]["role"] == "raw" or messages[-1]["role"] == "assistant":
            skip_final = True
        if messages[-1]["role"] == "assistant":
            modifiers[-1]["skip_postamble"] = True
            skip_postamble = len(messages) - 1
        if messages[0]["role"] == "system" and len(messages) > 1 and "system" not in formatter["roles"] and force_system:
            modifiers[0]["skip_postamble"] = True
            modifiers[1]["skip_preamble"] = True
            fake_system = True

        prompt=""
        if not skip_bos:
            prompt = formatter["bos"]
        skip_last = False
        for i in range(len(messages)):
            el = messages[i]
            if el["role"] not in formatter["roles"]:
                if el["role"] == "system" and force_system:
                     pass
                else:
                     continue

            if el["role"] == "raw":
                val = self.apply_format_templates(el["content"])
                #print(val,end="")
                prompt = prompt + val
            else:
                if not modifiers[i]["skip_preamble"]:
                    if "role_string" in formatter and el["role"] in formatter["role_string"]:
                         prompt = prompt + formatter["role_string"][el["role"]]
                    else:
                         role_name = formatter["assistant_name"] if el["role"] == "assistant" else el["role"]
                         role_name = formatter["system_name"] if el["role"] == "system" else role_name
                         role_name = formatter["user_name"] if el["role"] == "user" else role_name
                         prompt = prompt + formatter["bor"] + role_name + formatter["eor"]
                prompt = prompt + el["content"]
                if i == 0 and fake_system:
                    prompt += "\n\n"
                if not modifiers[i]["skip_postamble"]:
                    if "role_eom" in formatter and el["role"] in formatter["role_eom"] :
                        prompt = prompt + formatter["role_eom"][el["role"]]
                    else:
                        prompt = prompt + formatter["eom"]
        if not skip_final:
            if "role_string" in formatter and el["role"] in formatter["role_string"]:
                prompt = prompt + formatter["role_string"]["assistant"]
            else:
                prompt = prompt + formatter["bor"] + formatter["assistant_name"] + formatter["eor"]
        if "lf" in formatter:
            pass
            #prompt = prompt.replace("\n",formatter["lf"])
#        print(prompt)



        #    input_string += "\n"
        return prompt
    



## questa è la parte che non ha bisongno di conoscere il modello

class PromptBuilder:
    def __init__(self):
        self.formatter = Formatter()
        self.sysprompt = "You are a helpful assistant"
        self.force_system=False
        self.reset()
    
    def _check_special_tokens(self,m):
        is_raw = check_special_tokens(m)
        return is_raw
 
    def set_param(self,name,val):
        if name== "force_system":
             self.force_system = val
        elif name== "sysprompt":
             self.sysprompt = val
             self.reset()

    def _build(self):

        text_prompt = self.formatter.build_prompt(self.messages,force_system=self.force_system)
#        print(text_prompt)
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

        if  is_raw:
            try:
                self.messages = parse_raw(message)
            except:
                self.messages = [{"role":"raw","content":str(m)}]
        else:
            self.messages.append({"role":role,"content":str(m)})
        #print(self.messages)
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
