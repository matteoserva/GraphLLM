#from .parser import parse_raw, check_special_tokens
from transformers import AutoTokenizer
import copy

class FormatterHF:
    def __init__(self):
        self.hf_formatter = None

    def load_hf_model(self, model_name):
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
        elif model_name.lower().startswith("mistral-small"):
            tokenizer_path = "tokenizers/Mistral-Small-Instruct-2409"
        elif model_name.lower().startswith("_mistral-nemo"):
            tokenizer_path = "tokenizers/mistral-nemo"
        elif model_name.lower().startswith("_codegeex"):
            tokenizer_path = "/home/matteo/tmp/models_cache/codegeex4-all-9b"
        elif model_name.lower().startswith("_qwen2.5"):
            tokenizer_path = "tokenizers/Qwen2.5-32B-Instruct"
        elif model_name.lower().startswith("_qwen2"):
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

    def load_model(self, model_name):
        self.hf_formatter = self.load_hf_model(model_name)
        if self.hf_formatter:
            return True
        return False

    def build_prompt(self, messages, force_system=False, **kwargs):
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
                messages[1]["content"] = messages[0]["content"] + "\n\n" + messages[1]["content"]
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
            # messages = messages[1:]

        if raw_prompt is None:
            input_string = self.tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)
        else:
            if len(messages) == 1:
                input_string = raw_prompt
            else:
                assistant_response = messages[1]["content"]
                placeholder_string = "<<<<|>>>>PLACEHOLDER<<<|>>>"
                messages[0]["role"] = "user"
                messages[0]["content"] = "AAAA"
                messages[1]["content"] = placeholder_string
                input_string = self.tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)

                el = input_string.find(placeholder_string) + len(placeholder_string)
                input_string = raw_prompt + assistant_response + input_string[el:]


        if assistant_prompt is not None:
            input_string = input_string + assistant_prompt

        return input_string





