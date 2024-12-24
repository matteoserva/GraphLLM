import jinja2
from jinja2.ext import Extension
from jinja2.sandbox import ImmutableSandboxedEnvironment

class FormatterJinja:
    def __init__(self):
        self.jinja_env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=[jinja2.ext.loopcontrols])


    def load_template(self,chat_template):
        try:
            tokenizer = self.jinja_env.from_string(chat_template)
            messages = [
                {"role": "system", "content": "<<<SYSTEM>>>"},
                {"role": "user", "content": "<<<USER>>>"},
                {"role": "assistant", "content": "<<<ASSISTANT>>>"},
                {"role": "user", "content": "<<<USER2>>>"},
            ]
            rendered = tokenizer.render(messages=messages, add_generation_prompt=True)
        except:
            return False
        return False

    def build_prompt(self, messages, force_system=False):
        pass