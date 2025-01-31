
placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"


class FormatterLlamacpp:
    def __init__(self):

        self.tokenizer = None
        self.has_system = False
        self.optional_system = False

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

        return False

    def build_prompt_j(self, messages, force_system=False, custom_sysprompt=False, **kwargs):

        rendered = ""

        if messages[0]["role"] == "system" and (not custom_sysprompt) and self.optional_system:
            messages = messages[1:]

        updated_messages = [el for el in messages]

        if messages[0]["role"] == "raw":
            updated_messages[0] = {"role": "user", "content": "<<<RAW_TEMPLATE1>>>"}
            if len(messages) > 1:
                assert (messages[1]["role"] == "assistant")
                updated_messages[1] = {"role": "assistant", "content": "<<<RAW_TEMPLATE2>>>" + messages[1]["content"]}
            else:
                updated_messages.append({"role": "assistant", "content": "<<<RAW_TEMPLATE2>>>"})

        if messages[0]["role"] == "system" and not self.has_system and force_system:
            assert (messages[1]["role"] == "user")
            updated_messages[1] = {"role": "user", "content": messages[0]["content"] + "\n\n" + messages[1]["content"]}
            updated_messages = updated_messages[1:]

        if updated_messages[-1]["role"] == "assistant":
            rendered += self.apply_template(messages=updated_messages[:-1])
            rendered += updated_messages[-1]["content"]
        else:
            rendered += self.apply_template(messages=updated_messages)

        if messages[0]["role"] == "raw":
            pos = rendered.find("<<<RAW_TEMPLATE2>>>") + len("<<<RAW_TEMPLATE2>>>")
            a = messages[0]["content"].replace("{p:bos}\n", "")
            a = a.replace("{p:bos}", "")
            rendered = a + rendered[pos:]


        return rendered


    def build_prompt(self, *args, **kwargs):

        prompt_j = self.build_prompt_j(*args, **kwargs)
        return prompt_j

