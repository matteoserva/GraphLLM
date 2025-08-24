
placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

def evaluate_template(self):
    messages = [
        {"role": "system", "content": placeholder_system},
        {"role": "user", "content": placeholder_user},
        {"role": "assistant", "content": placeholder_assistant},
        {"role": "user", "content": placeholder_user2},
    ]
    rendered = self._render(messages=messages, bos_token="<<<BOS>>>", eos_token="<<<EOS>>>")
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
            rendered = self._render(messages=messages, bos_token="<<<BOS>>>", eos_token="<<<EOS>>>")
            self.optional_system = placeholder_user in rendered
        except:
            pass