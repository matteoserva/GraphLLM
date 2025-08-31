


"""
self.transitions = {"init":{}, "raw": {} , "system": {}, "user": {} , "assistant": {}}


def load_template_with_system(self, rendered):
    pos = rendered.find(placeholder_system)
    t = rendered[:pos]
    self.transitions["init"]["system"] = t

    posu = rendered.find(placeholder_user)
    t = rendered[pos + len(placeholder_system):posu]
    self.transitions["system"]["user"] = t

    messages = [{"role": "user", "content": placeholder_user}]
    r2 = self.tokenizer.render(messages=messages, add_generation_prompt=True, strftime_now=self._strftime)
    posu = r2.find(placeholder_user)
    t = r2[:posu]
    self.transitions["init"]["user"] = t


def load_template_without_system(self, rendered):
    pos = rendered.find(placeholder_user)
    t = rendered[:pos]
    self.transitions["init"]["system"] = t
    self.transitions["system"]["user"] = "\n\n"

    self.transitions["init"]["user"] = t


def load_template_assistant(self, rendered):
    pos = rendered.find(placeholder_user)
    pos2 = rendered.find(placeholder_assistant)
    t = rendered[pos + len(placeholder_user):pos2]
    self.transitions["user"]["assistant"] = t

    pos = rendered.find(placeholder_assistant)
    pos2 = rendered.find(placeholder_user2)
    t = rendered[pos + len(placeholder_assistant):pos2]
    self.transitions["assistant"]["user"] = t


def load_template_raw(self, rendered):
    self.transitions["init"]["raw"] = ""
    self.transitions["raw"]["assistant"] = ""




def ...
messages = [
                {"role": "system", "content": placeholder_system},
                {"role": "user", "content": placeholder_user},
                {"role": "assistant", "content": placeholder_assistant},
                {"role": "user", "content": placeholder_user2},
            ]
            rendered = self.tokenizer.render(messages=messages, add_generation_prompt=True,strftime_now = self._strftime)

            if self.has_system:
                self.load_template_with_system(rendered)
            else:
                self.load_template_without_system(rendered)

            self.load_template_assistant(rendered)
            self.load_template_raw(rendered)

if self.has_bos_token:
    self.transitions["init"]["system"] = model_props["bos_token"] + self.transitions["init"]["system"]
    self.transitions["init"]["user"] = model_props["bos_token"] + self.transitions["init"]["user"]
    self.bos_token = model_props["bos_token"]

    def build_prompt_sm(self, messages, force_system=False,**kwargs):
        builder_state="init"
        current_prompt = ""

        for el in messages:
            new_role = el["role"]
            if new_role == "system" and (not force_system) and (not self.has_system):
                continue

            current_prompt += self.transitions[builder_state][new_role]
            current_prompt += el["content"]
            builder_state = new_role

        if builder_state != "assistant":
            current_prompt += self.transitions[builder_state]["assistant"]
            builder_state = "assistant"

        return current_prompt

"""