import jinja2
from jinja2.ext import Extension
from jinja2.sandbox import ImmutableSandboxedEnvironment

import datetime
from modules.formatter.formatter_common import evaluate_template

class FormatterJinja:
    def __init__(self):
        self.jinja_env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=[jinja2.ext.loopcontrols])
        self.tokenizer = None
        self.has_system = False
        self.optional_system = False
        self.has_bos_token = False
        self.bos_token = ""
        self.has_eos_token = False
        self.multi_turn = False

    def _render(self,*args,**kwargs):
        kwargs["strftime_now"] = self._strftime
        kwargs["bos_token"] = self.bos_token
        rendered = self.tokenizer.render(*args,**kwargs)
        return rendered

    @staticmethod
    def _strftime(x):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return current_date


    def load_template(self,model_props):
        #model_name = model_props["model_name"]
        chat_template = model_props.get("chat_template",None)
        self.bos_token = model_props.get("bos_token","")

        if not chat_template:
            return False
        try:
            self.tokenizer = self.jinja_env.from_string(chat_template)
            template_props = evaluate_template(self._render)
            for el in template_props:
                setattr(self,el,template_props[el])
        except:
            return False
        
        if not self.multi_turn:
            return False

        if not self.has_system:
            pass

        if self.has_bos_token and len(model_props.get("bos_token","")) == 0 :
            return False

        return template_props
