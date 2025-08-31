
def process_model_props(model_props):
    model_name = model_props["model_name"]

    extra_props = {}

    extra_props["enable_formatter_template"] = model_props.get("chat_template", None) is not None
    extra_props["enable_formatter_llamacpp"] = "apply_template" in model_props
    extra_props["model_type"] = "other"

    if model_name.lower().find("deepseek-r1") == 0:
        extra_props["model_type"] = "deepseek-r1"
        extra_props["optional_system"] = True

    if model_name.lower().find("gpt-oss") >= 0:
        extra_props["model_type"] = "gpt-oss"

    return extra_props

def apply_generation_prompt_fixes(self, rendered):
    if rendered.endswith("<think>\n"):
        rendered = rendered[:-8]
    rendered += self.generation_prompt_prefix
    return rendered

def preprocess_messages_list(messages, extra_props):
    updated_messages = []

    if extra_props["model_type"] == "gpt-oss":
        for el in messages[:-1]:
            if el["role"] == "assistant":
                el["content"] = el["content"].split("<|channel|>final<|message|>")[-1]
            updated_messages.append(el)
        updated_messages.append(messages[-1])
    else:
        for el in messages:
            updated_messages.append(el)
    return updated_messages

def format_prefill_message(message, extra_props):
    if extra_props["model_type"] == "gpt-oss":
        if message.startswith("<|channel|>"):
            formatted = message
        else:
            formatted = "<|channel|>final<|message|>" + message
    else:
        formatted = message

    return formatted