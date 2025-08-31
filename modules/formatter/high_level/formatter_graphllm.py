
class RendererGraphLLM:
    def __init__(self):
        pass

    def build_prompt_j(self, messages, *args, **kwargs):
        decorated_messages = ["{p:" + el["role"] + "}\n" + el["content"] + "{p:eom}" for el in messages]
        text_prompt = "{p:bos}\n\n" + "\n\n".join(decorated_messages)
        return text_prompt