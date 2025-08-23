import datetime

TAG_RAW_TEMPLATE = "<<<RAW_TEMPLATE2>>>"
placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

class TemplateRenderer():
    def __init__(self,render_function):
        self.render_function = render_function
        self.has_system = False
        self.optional_system = False
        self.multi_turn = False
        self.generation_prompt_prefix = ""

    def _strftime(self,x):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return current_date

    def _render(self,*args,**kwargs):
        return self.render_function(*args,**kwargs)

    def apply_generation_prompt_fixes(self, rendered):
        if rendered.endswith("<think>\n"):
            rendered = rendered[:-8]
        rendered += self.generation_prompt_prefix
        return rendered

    def _evaluate_template(self):
        messages = [
            {"role": "system", "content": placeholder_system},
            {"role": "user", "content": placeholder_user},
            {"role": "assistant", "content": placeholder_assistant},
            {"role": "user", "content": placeholder_user2},
        ]
        rendered = self._render(messages,bos_token = "<<<BOS>>>",eos_token = "<<<EOS>>>")
        self.has_system = placeholder_system in rendered
        self.multi_turn = placeholder_user2 in rendered
        self.has_bos_token = "<<<BOS>>>" in rendered
        self.has_eos_token = "<<<EOS>>>" in rendered

        if self.has_system:
            messages = [
                {"role": "user", "content": placeholder_user},
            ]
            self.optional_system = False
            try:
                rendered = self._render(messages,bos_token = "<<<BOS>>>",eos_token = "<<<EOS>>>")
                self.optional_system = placeholder_user in rendered
            except:
                pass

    def build_prompt_j(self, messages, force_system=False, custom_sysprompt=False, **kwargs):
        rendered = ""

        if messages[0]["role"] == "system" and (not custom_sysprompt) and self.optional_system:
            messages = messages[1:]

        updated_messages = [el for el in messages]

        if messages[0]["role"] == "raw":
            updated_messages[0] = {"role": "user", "content": "<<<UNUSED_RAW_TEMPLATE1>>>"}
            if len(messages) > 1:
                assert (messages[1]["role"] == "assistant")
                updated_messages[1] = {"role": "assistant", "content": TAG_RAW_TEMPLATE + messages[1]["content"]}
            else:
                updated_messages.append({"role": "assistant", "content": TAG_RAW_TEMPLATE})

        if messages[0]["role"] == "system" and not self.has_system and (force_system or custom_sysprompt):
            assert (messages[1]["role"] == "user")
            updated_messages[1] = {"role": "user", "content": messages[0]["content"] + "\n\n" + messages[1]["content"]}
            updated_messages = updated_messages[1:]

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