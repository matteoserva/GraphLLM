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
        rendered += self.tokenizer.render(messages=updated_messages[:-1], add_generation_prompt=True)
        rendered += self.generation_prompt_prefix
        rendered += updated_messages[-1]["content"]
    else:
        rendered += self.tokenizer.render(messages=updated_messages, add_generation_prompt=True)
        rendered += self.generation_prompt_prefix

    if messages[0]["role"] == "raw":
        pos = rendered.find("<<<RAW_TEMPLATE2>>>") + len("<<<RAW_TEMPLATE2>>>")
        a = messages[0]["content"].replace("{p:bos}\n", "")
        a = a.replace("{p:bos}", "")
        rendered = a + rendered[pos:]

    if self.has_bos_token:
        rendered = self.bos_token + rendered

    return rendered