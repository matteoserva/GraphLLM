import jinja2
from jinja2.ext import Extension
from jinja2.sandbox import ImmutableSandboxedEnvironment
from sympy import false
from .renderer_template import TemplateRenderer
import datetime

placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

class FormatterJinja:
    def __init__(self):
        self.jinja_env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=[jinja2.ext.loopcontrols])
        self.tokenizer = None
        self.has_system = False
        self.optional_system = False

        self.renderer = TemplateRenderer(self._render)

    def _render(self,*args,**kwargs):
        kwargs["strftime_now"] = self._strftime
        rendered = self.tokenizer.render(*args,**kwargs)
        return rendered


    def _evaluate_template(self):
        messages = [
            {"role": "system", "content": placeholder_system},
            {"role": "user", "content": placeholder_user},
            {"role": "assistant", "content": placeholder_assistant},
            {"role": "user", "content": placeholder_user2},
        ]
        rendered = self.tokenizer.render(messages=messages, add_generation_prompt=True,bos_token = "<<<BOS>>>",eos_token = "<<<EOS>>>",strftime_now = self._strftime)
        self.has_system = placeholder_system in rendered
        self.multi_turn = "<<<USER2>>>" in rendered
        self.has_bos_token = "<<<BOS>>>" in rendered
        self.has_eos_token = "<<<EOS>>>" in rendered
        self.generation_prompt_prefix = ""

        if self.has_system:
            messages = [
                {"role": "user", "content": placeholder_user},
            ]
            self.optional_system = False
            try:
                rendered = self.tokenizer.render(messages=messages, add_generation_prompt=True,bos_token = "<<<BOS>>>",eos_token = "<<<EOS>>>",strftime_now = self._strftime)
                self.optional_system = placeholder_user in rendered
            except:
                pass

    def _strftime(self,x):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return current_date

    def load_template(self,model_props):
        model_name = model_props["model_name"]
        chat_template = model_props.get("chat_template",None)
        if not chat_template:
            return False
        try:
            self.tokenizer = self.jinja_env.from_string(chat_template)
            self._evaluate_template()

        except:
            return False
        
        if not self.multi_turn:
            return False

        if not self.has_system:
            pass

        if self.has_bos_token and len(model_props.get("bos_token","")) == 0 :
            return False

        if self.has_bos_token:
            self.bos_token = model_props["bos_token"]

        return True

    def build_prompt(self, *args,**kwargs):
        #prompt_sm = self.build_prompt_sm(*args,**kwargs)
        prompt_j = self.renderer.build_prompt_j(self, *args,**kwargs)
        return prompt_j

def execute_test_full(tokenizer_path):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    chat_template = tokenizer.chat_template

    formatter = FormatterJinja()
    formatter.load_template({"model_name": "test", "chat_template": chat_template})
    messages = [
        {"role": "system", "content": "<<<SYSTEM>>>"},
        {"role": "user", "content": "<<<USER>>>"},
        {"role": "assistant", "content": "<<<ASSISTANT>>>"},
        {"role": "user", "content": "<<<USER2>>>"},
    ]
    generated_prompt = formatter.build_prompt(messages)
    reference_prompt = tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)
    print("### TEST FULL: \n" + generated_prompt)
    test_passed = generated_prompt == reference_prompt
    #assert (test_passed)

    messages = [
        {"role": "raw", "content": "<<<RAW>>>"},
        {"role": "assistant", "content": "<<<PREFILL>>>"},
        {"role": "user", "content": "<<<USER2>>>"},
    ]
    generated_prompt = formatter.build_prompt(messages)
    print("### TEST RAW: \n" + generated_prompt)
    return True

def execute_test_simple(tokenizer_path):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    chat_template = tokenizer.chat_template

    formatter = FormatterJinja()
    formatter.load_template({"model_name": "test", "chat_template": chat_template, "bos_token": "{p:bos}"})
    messages = [
        {"role": "system", "content": "<<<SYSTEM>>>"},
        {"role": "user", "content": "<<<USER>>>"},
        {"role": "assistant", "content": "<<<ASSISTANT>>>"},
        {"role": "user", "content": "<<<USER2>>>"},
    ]
    generated_prompt = formatter.build_prompt(messages,force_system=True)
    reference_prompt = tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)
    print("### TEST SIMPLE FORCED: \n" + generated_prompt)
    test_passed = generated_prompt == reference_prompt

    generated_prompt = formatter.build_prompt(messages, force_system=False)
    print("### TEST SIMPLE NOSYSTEM: \n" + generated_prompt)
    # assert (test_passed)

if __name__ == "__main__":
    from transformers import AutoTokenizer

    tokenizer_path = "tokenizers/Qwen2.5-32B-Instruct"
    execute_test_full(tokenizer_path)
    tokenizer_path = "tokenizers/phi3-mini"
    execute_test_simple(tokenizer_path)

    pass