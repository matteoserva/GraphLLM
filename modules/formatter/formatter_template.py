import datetime

TAG_RAW_TEMPLATE = "<<<RAW_TEMPLATE2>>>"
placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

DEFAULT_SYSPROMPT = "You are a helpful assistant"

class TemplateRenderer():
    def __init__(self,formatter):
        self.formatter = formatter

        self.has_system = False
        self.optional_system = False
        self.multi_turn = False
        self.generation_prompt_prefix = ""
        self.has_bos_token = False
        self.has_eos_token = False

    def _render(self,*args,**kwargs):
        return self.formatter._render(*args,**kwargs)

    def apply_generation_prompt_fixes(self, rendered):
        if rendered.endswith("<think>\n"):
            rendered = rendered[:-8]
        rendered += self.generation_prompt_prefix
        return rendered

    def load_template(self,model_props):
        template_props = self.formatter.load_template(model_props)
        if not template_props:
            return False
        for el in template_props:
            setattr(self, el, template_props[el])
        return True

    def build_prompt(self, messages, **kwargs):
        rendered = ""

        updated_messages = [el for el in messages]

        if messages[0]["role"] == "raw":
            updated_messages[0] = {"role": "user", "content": "<<<UNUSED_RAW_TEMPLATE1>>>"}
            if len(messages) > 1:
                assert (messages[1]["role"] == "assistant")
                updated_messages[1] = {"role": "assistant", "content": TAG_RAW_TEMPLATE + messages[1]["content"]}
            else:
                updated_messages.append({"role": "assistant", "content": TAG_RAW_TEMPLATE})

        if messages[0]["role"] == "system" and not self.has_system:
            assert (messages[1]["role"] == "user")
            updated_messages[1] = {"role": "user", "content": messages[0]["content"] + "\n\n" + messages[1]["content"]}
            updated_messages = updated_messages[1:]

        if messages[0]["role"] == "user" and self.has_system and not self.optional_system:
            updated_messages.insert(0,{"role": "user", "content":DEFAULT_SYSPROMPT})

        if updated_messages[-1]["role"] == "assistant":
            rendered += self._render(messages=updated_messages[:-1], add_generation_prompt=True)
            rendered = self.apply_generation_prompt_fixes(rendered)
            rendered += updated_messages[-1]["content"]
        else:
            rendered += self._render(messages=updated_messages, add_generation_prompt=True)
            rendered = self.apply_generation_prompt_fixes(rendered)

        if messages[0]["role"] == "raw":
            pos = rendered.find(TAG_RAW_TEMPLATE) + len(TAG_RAW_TEMPLATE)
            a = messages[0]["content"].replace("{p:bos}\n", "")
            a = a.replace("{p:bos}", "")
            rendered = a + rendered[pos:]

        if self.has_bos_token:
            rendered = self.bos_token + rendered

        return rendered