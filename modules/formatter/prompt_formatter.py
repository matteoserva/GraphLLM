
#from transformers import AutoTokenizer
#from .formatter_hf import FormatterHF
from modules.formatter.high_level.formatter_custom import FormatterCustom
from modules.formatter.low_level.formatter_llamacpp import FormatterLlamacpp
from modules.formatter.high_level.formatter_template import TemplateRenderer
from .model_parameters import process_model_props

try:
    from modules.formatter.low_level.formatter_jinja import FormatterJinja
except:
    pass

import copy



class Formatter:
    def __init__(self):
        self.formatter = None
        self.model_name = None
        self.use_template = False

    def load_model(self, model_props):
        if not isinstance(model_props, dict):
            model_props = {"model_name": model_props, "chat_template": None}

        extra_props = process_model_props(model_props)

        model_name = model_props["model_name"]
        chat_template = model_props.get("chat_template", None)

        self.model_name = model_name

        """
        if "use_hf" in model_props: #this is not used
            try:
                self.formatter = FormatterHF()
                if self.formatter.load_model(model_name):
                    pass
            except:
                pass
        """

        if extra_props["enable_formatter_template"]:
            try:
                ll_formatter = FormatterJinja()
                self.formatter = TemplateRenderer(ll_formatter)
                if self.formatter.load_template(model_props, extra_props):
                        return True
            except:
                pass

        if extra_props["enable_formatter_llamacpp"]:
            try:
                ll_formatter = FormatterLlamacpp()
                self.formatter = TemplateRenderer(ll_formatter)
                if self.formatter.load_template(model_props, extra_props):
                    return True
            except:
                pass

        # fallback
        self.formatter = FormatterCustom()
        self.formatter.load_model(model_name)

        return True

    def build_prompt(self, messages, force_system=False, **kwargs):
        messages = copy.deepcopy(messages)

        prompt = self.formatter.build_prompt(messages, force_system=force_system, **kwargs)
        # workaround per deepseek
        if self.model_name.lower().startswith("deepseek") and prompt.endswith("Assistant: "):
            prompt = prompt[:-1]
            # workaround per deepseek
        if self.model_name.lower().startswith("glm") and prompt.endswith("<|assistant|>\n") and self.model_name.lower().find("0414") < 0:
            prompt = prompt[:-1]

        return prompt