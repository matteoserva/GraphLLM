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

    def _strftime(self,x):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return current_date

    def load_template(self,model_props):
        #model_name = model_props["model_name"]
        chat_template = model_props.get("chat_template",None)
        if not chat_template:
            return False
        try:
            self.tokenizer = self.jinja_env.from_string(chat_template)
            self.renderer._evaluate_template()

        except:
            return False
        
        if not self.renderer.multi_turn:
            return False

        if not self.renderer.has_system:
            pass

        if self.renderer.has_bos_token and len(model_props.get("bos_token","")) == 0 :
            return False


        return True

    def build_prompt(self, *args,**kwargs):
        #prompt_sm = self.build_prompt_sm(*args,**kwargs)
        prompt_j = self.renderer.build_prompt_j(*args,**kwargs)
        return prompt_j
