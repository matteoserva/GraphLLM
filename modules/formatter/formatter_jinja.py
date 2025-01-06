import jinja2
from jinja2.ext import Extension
from jinja2.sandbox import ImmutableSandboxedEnvironment

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

    def load_template_to_assistant(self,rendered):
        pos = rendered.find(placeholder_user)
        pos2 = rendered.find(placeholder_assistant)
        t = rendered[pos + len(placeholder_user):pos2]
        self.transitions["user"]["assistant"] = t

        pos = rendered.find(placeholder_assistant)
        pos2 = rendered.find(placeholder_user2)
        t = rendered[pos + len(placeholder_assistant):pos2]
        self.transitions["assistant"]["user"] = t

    def load_template(self,chat_template):

        try:
            self.tokenizer = self.jinja_env.from_string(chat_template)
            messages = [
                {"role": "system", "content": placeholder_system},
                {"role": "user", "content": placeholder_user},
                {"role": "assistant", "content": placeholder_assistant},
                {"role": "user", "content": placeholder_user2},
            ]
            rendered = self.tokenizer.render(messages=messages, add_generation_prompt=True)
            self.has_system = placeholder_system in rendered
            self.multi_turn = "<<<USER2>>>" in rendered

            if self.has_system:
                self.load_template_with_system(rendered)
            else:
                self.load_template_without_system(rendered)

            self.load_template_to_assistant(rendered)


        except:
            return False
        return False

    def build_prompt(self, messages, force_system=False):
        builder_state="init"
        current_prompt = ""

        for el in messages:
            new_role = el["role"]
            current_prompt += self.transitions[builder_state][new_role]
            current_prompt += el["content"]
            builder_state = new_role

        if builder_state != "assistant":
            current_prompt += self.transitions[builder_state]["assistant"]
            builder_state = "assistant"

        return current_prompt


if __name__ == "__main__":
    from transformers import AutoTokenizer

    tokenizer_path = "tokenizers/Qwen2.5-32B-Instruct"
    #tokenizer_path = "tokenizers/phi3-mini"
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
    chat_template = tokenizer.chat_template

    formatter = FormatterJinja()
    formatter.load_template(chat_template)
    messages = [
        {"role": "system", "content": "<<<SYSTEM>>>"},
        {"role": "user", "content": "<<<USER>>>"},
        {"role": "assistant", "content": "<<<ASSISTANT>>>"},
        {"role": "user", "content": "<<<USER2>>>"},
    ]
    generated_prompt = formatter.build_prompt(messages)
    reference_prompt = tokenizer.apply_chat_template(messages, add_special_tokens=True, add_generation_prompt=True, tokenize=False)

    pass