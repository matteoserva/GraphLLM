from .common_utils import readfile
from ..formatter import Formatter
from ..formatter import solve_templates
import copy
from ..fake_python import PythonInterpreter
from ._other import *

def try_solve_files(cl_args):
    for i, el in enumerate(cl_args):
        try:
            cl_args[i] = readfile(el)
        except:
            pass
    return cl_args


def get_formatter(props):
    print(props["default_generation_settings"]["model"])
    model_path = props["default_generation_settings"]["model"]
    model_name = model_path.split("/")[-1]

    formatter = Formatter()
    formatter.load_model(model_name)
    return formatter


def apply_format_templates(formatter, prompt):
    return formatter.apply_format_templates(prompt)


def build_prompt(formatter, messages):
    return formatter.build_prompt(messages)