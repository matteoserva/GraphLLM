import jinja2
from jinja2.ext import Extension
from jinja2.sandbox import ImmutableSandboxedEnvironment
from sympy import false

placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

class FormatterJinja:
    def __init__(self):
        self.jinja_env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=[jinja2.ext.loopcontrols])
        self.tokenizer = None
        self.has_system = False

        self.transitions = {"init":{}, "raw": {} , "system": {}, "user": {} , "assistant": {}}


    def load_template_with_system(self,rendered):
        pos = rendered.find(placeholder_system)
        t = rendered[:pos]
        self.transitions["init"]["system"] = t

        posu = rendered.find(placeholder_user)
        t = rendered[pos + len(placeholder_system):posu]
        self.transitions["system"]["user"] = t

        messages = [{"role": "user", "content": placeholder_user}]
        r2 = self.tokenizer.render(messages=messages, add_generation_prompt=True)
        posu = r2.find(placeholder_user)
        t = r2[:posu]
        self.transitions["init"]["user"] = t

    def load_template_without_system(self,rendered):
        pos = rendered.find(placeholder_user)
        t = rendered[:pos]
        self.transitions["init"]["system"] = t
        self.transitions["system"]["user"] = "\n\n"

        self.transitions["init"]["user"] = t

    def load_template_assistant(self,rendered):
        pos = rendered.find(placeholder_user)
        pos2 = rendered.find(placeholder_assistant)
        t = rendered[pos + len(placeholder_user):pos2]
        self.transitions["user"]["assistant"] = t

        pos = rendered.find(placeholder_assistant)
        pos2 = rendered.find(placeholder_user2)
        t = rendered[pos + len(placeholder_assistant):pos2]
        self.transitions["assistant"]["user"] = t

    def load_template_raw(self,rendered):
        self.transitions["init"]["raw"] = ""
        self.transitions["raw"]["assistant"] = ""

    def _evaluate_template(self):
        messages = [
            {"role": "system", "content": placeholder_system},
            {"role": "user", "content": placeholder_user},
            {"role": "assistant", "content": placeholder_assistant},
            {"role": "user", "content": placeholder_user2},
        ]
        rendered = self.tokenizer.render(messages=messages, add_generation_prompt=True,bos_token = "<<<BOS>>>")
        self.has_system = placeholder_system in rendered
        self.multi_turn = "<<<USER2>>>" in rendered
        self.has_bos_token = "<<<BOS>>>" in rendered


    def load_template(self,model_props):
        model_name = model_props["model_name"]
        chat_template = model_props.get("chat_template",None)

        try:
            self.tokenizer = self.jinja_env.from_string(chat_template)
            self._evaluate_template()
            messages = [
                {"role": "system", "content": placeholder_system},
                {"role": "user", "content": placeholder_user},
                {"role": "assistant", "content": placeholder_assistant},
                {"role": "user", "content": placeholder_user2},
            ]
            rendered = self.tokenizer.render(messages=messages, add_generation_prompt=True)

            if self.has_system:
                self.load_template_with_system(rendered)
            else:
                self.load_template_without_system(rendered)

            self.load_template_assistant(rendered)
            self.load_template_raw(rendered)

        except:
            return False
        
        if not self.multi_turn:
            return False

        if not self.has_system:
            pass

        if (len(model_props.get("bos_token","")) > 0) != self.has_bos_token :
            return False

        if self.has_bos_token:
            self.transitions["init"]["system"] = model_props["bos_token"] + self.transitions["init"]["system"]
            self.transitions["init"]["user"] = model_props["bos_token"] + self.transitions["init"]["user"]
            self.bos_token = model_props["bos_token"]

        if model_name.lower().find("deepseek-r1") == 0:
            return True

        return False

    def build_prompt_j(self, messages, force_system=False):

        rendered = ""
        updated_messages = [el for el in messages]

        if messages[0]["role"] == "raw":
            updated_messages[0]  = {"role": "user", "content" : "<<<RAW_TEMPLATE1>>>"}
            if len(messages) > 1:
                assert(messages[1]["role"] == "assistant")
                updated_messages[1] = {"role": "assistant", "content" : "<<<RAW_TEMPLATE2>>>" + messages[1]["content"]}
            else:
                updated_messages.append({"role": "assistant", "content": "<<<RAW_TEMPLATE2>>>"})

        if messages[0]["role"] == "system" and not self.has_system and force_system:
            assert (messages[1]["role"] == "user")
            updated_messages[1] = {"role": "user", "content" : messages[0]["content"] + "\n\n" + messages[1]["content"]}
            updated_messages = updated_messages[1:]


        if updated_messages[-1]["role"] == "assistant":
            rendered += self.tokenizer.render(messages=updated_messages[:-1], add_generation_prompt=True)
            rendered += updated_messages[-1]["content"]
        else:
            rendered += self.tokenizer.render(messages=updated_messages, add_generation_prompt=True)

        if messages[0]["role"] == "raw":
            pos = rendered.find("<<<RAW_TEMPLATE2>>>" ) + len("<<<RAW_TEMPLATE2>>>")
            a = messages[0]["content"] .replace("{p:bos}\n", "")
            a = a.replace("{p:bos}", "")
            rendered = a + rendered[pos:]

        if self.has_bos_token:
            rendered = self.bos_token + rendered


        return rendered


    def build_prompt_sm(self, messages, force_system=False):
        builder_state="init"
        current_prompt = ""

        for el in messages:
            new_role = el["role"]
            if new_role == "system" and (not force_system) and (not self.has_system):
                continue

            current_prompt += self.transitions[builder_state][new_role]
            current_prompt += el["content"]
            builder_state = new_role

        if builder_state != "assistant":
            current_prompt += self.transitions[builder_state]["assistant"]
            builder_state = "assistant"

        return current_prompt

    def build_prompt(self,*args,**kwargs):
        prompt_sm = self.build_prompt_sm(*args,**kwargs)
        prompt_j = self.build_prompt_j(*args,**kwargs)
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