from .renderer_template import TemplateRenderer

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

    def _evaluate_template(self):
        messages = [
            {"role": "system", "content": placeholder_system},
            {"role": "user", "content": placeholder_user},
            {"role": "assistant", "content": placeholder_assistant},
            {"role": "user", "content": placeholder_user2},
        ]
        rendered = self.apply_template(messages)
        self.has_system = placeholder_system in rendered
        self.multi_turn = "<<<USER2>>>" in rendered

        if self.has_system:
            messages = [
                {"role": "user", "content": placeholder_user},
            ]
            self.optional_system = False
            try:
                rendered = self._render(messages)
                self.optional_system = placeholder_user in rendered
            except:
                pass

    def load_template(self, model_props):
        self.model_props = model_props
        model_name = model_props["model_name"]
        self.apply_template = model_props.get("apply_template", None)
        if not self.apply_template :
            return False

        try:
            self._evaluate_template()
        except:
            return False

        if not self.multi_turn:
            return False

        if not self.has_system:
            pass

        if model_name.lower().find("deepseek-r1") == 0:
            self.optional_system = True
            return True

        if model_name.lower().find("mistral") == 0 and model_name.lower().find("instruct") >= 0:
            return True

        return True


    def build_prompt(self, *args, **kwargs):

        prompt_j = self.renderer.build_prompt_j(self, *args, **kwargs)
        return prompt_j

