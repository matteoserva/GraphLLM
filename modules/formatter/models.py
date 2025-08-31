
def process_model_props(model_props):
    model_name = model_props["model_name"]

    extra_props = {}

    extra_props["enable_formatter_template"] = model_props.get("chat_template", None) is not None
    extra_props["enable_formatter_llamacpp"] = "apply_template" in model_props

    if model_name.lower().find("deepseek-r1") == 0:
        extra_props["optional_system"] = True

    return extra_props
