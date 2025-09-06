
placeholder_system = "<<<SYSTEM>>>"
placeholder_user = "<<<USER>>>"
placeholder_assistant = "<<<ASSISTANT>>>"
placeholder_user2 = "<<<USER2>>>"

def evaluate_template(render_function):
    messages = [
        {"role": "system", "content": placeholder_system},
        {"role": "user", "content": placeholder_user},
        {"role": "assistant", "content": placeholder_assistant},
        {"role": "user", "content": placeholder_user2},
    ]
    rendered = render_function(messages=messages, bos_token="<<<BOS>>>", eos_token="<<<EOS>>>")
    template_props = {
        "has_system": placeholder_system in rendered,
        "multi_turn": placeholder_user2 in rendered,
        "has_bos_token": "<<<BOS>>>" in rendered,
        "has_eos_token": "<<<EOS>>>" in rendered
    }

    if template_props["has_system"]:
        messages = [
            {"role": "user", "content": placeholder_user},
        ]
        template_props["optional_system"] = False
        try:
            rendered = render_function(messages=messages, bos_token="<<<BOS>>>", eos_token="<<<EOS>>>")
            template_props["optional_system"] = placeholder_user in rendered
        except:
            pass

    return template_props