import datetime

class TemplateRenderer():
    def __init__(self,render_function):
        self._render = render_function

    def _strftime(self,x):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return current_date

    def apply_generation_prompt_fixes(self,formatter, rendered):
        if rendered.endswith("<think>\n"):
            rendered = rendered[:-8]
        rendered += formatter.generation_prompt_prefix
        return rendered

    def build_prompt_j(self,formatter, messages, force_system=False, custom_sysprompt=False, **kwargs):
        rendered = ""

        if messages[0]["role"] == "system" and (not custom_sysprompt) and formatter.optional_system:
            messages = messages[1:]

        updated_messages = [el for el in messages]

        if messages[0]["role"] == "raw":
            updated_messages[0] = {"role": "user", "content": "<<<RAW_TEMPLATE1>>>"}
            if len(messages) > 1:
                assert (messages[1]["role"] == "assistant")
                updated_messages[1] = {"role": "assistant", "content": "<<<RAW_TEMPLATE2>>>" + messages[1]["content"]}
            else:
                updated_messages.append({"role": "assistant", "content": "<<<RAW_TEMPLATE2>>>"})

        if messages[0]["role"] == "system" and not formatter.has_system and (force_system or custom_sysprompt):
            assert (messages[1]["role"] == "user")
            updated_messages[1] = {"role": "user", "content": messages[0]["content"] + "\n\n" + messages[1]["content"]}
            updated_messages = updated_messages[1:]

        if updated_messages[-1]["role"] == "assistant":
            rendered += self._render(messages=updated_messages[:-1], add_generation_prompt=True,strftime_now = self._strftime)
            rendered = self.apply_generation_prompt_fixes(formatter, rendered)
            rendered += updated_messages[-1]["content"]
        else:
            rendered += self._render(messages=updated_messages, add_generation_prompt=True,strftime_now = self._strftime)
            rendered = self.apply_generation_prompt_fixes(formatter, rendered)

        if messages[0]["role"] == "raw":
            pos = rendered.find("<<<RAW_TEMPLATE2>>>") + len("<<<RAW_TEMPLATE2>>>")
            a = messages[0]["content"].replace("{p:bos}\n", "")
            a = a.replace("{p:bos}", "")
            rendered = a + rendered[pos:]

        if formatter.has_bos_token:
            rendered = formatter.bos_token + rendered

        return rendered