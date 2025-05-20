from ..formatter import Formatter
from ..formatter import solve_templates

def solve_placeholders(base, confArgs, confVariables={}):
    for i in range(len(confArgs)):
        name = "{p:exec" + str(i + 1) + "}"
        val = confArgs[i]
        base = base.replace(name, val)
    for el in confVariables:
        name = "{p:" + el + "}"
        val = confVariables[el]
        base = base.replace(name, val)
    return base


def solve_prompt_args(prompt, prompt_args):
    annotated_args = [(0, el) for el in prompt_args]
    annotated_args = [(1, el) if isinstance(el, dict) else (an, el) for an, el in annotated_args]

    dict_args = [el for an, el in annotated_args if an == 1]
    text_args = [el for an, el in annotated_args if an == 0]

    m = prompt
    for el in dict_args:
        m = solve_placeholders(m, [], el)
    m, _ = solve_templates(m, text_args)
    m = solve_placeholders(m, text_args)
    return m