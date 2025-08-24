from .formatter_template import TemplateRenderer
from .formatter_common import evaluate_template

placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

class Renderer:
    def __init__(self, formatter):
        self.formatter = formatter

    def render(self,messages,*args,**kwargs):
        return self.formatter.apply_template(messages)

class FormatterLlamacpp:
    def __init__(self):

        self.tokenizer = None
        self.has_system = False
        self.optional_system = False
        self.generation_prompt_prefix = ""
        self.tokenizer = Renderer(self)
        self.has_bos_token = False
        self.renderer = TemplateRenderer(self._render)

    def _render(self,messages,*args,**kwargs):
        return self.apply_template(messages)

    def load_template(self, model_props):
        self.model_props = model_props
        model_name = model_props["model_name"]
        self.apply_template = model_props.get("apply_template", None)
        if not self.apply_template :
            return False

        try:
            template_props = evaluate_template(self._render)
            for el in template_props:
                setattr(self, el, template_props[el])
        except:
            return False

        if not self.renderer.multi_turn:
            return False

        if not self.renderer.has_system:
            pass

        if model_name.lower().find("deepseek-r1") == 0:
            self.optional_system = True
            return True

        if model_name.lower().find("mistral") == 0 and model_name.lower().find("instruct") >= 0:
            return True

        return template_props

