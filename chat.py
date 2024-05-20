#!/usr/bin/python3
import sys
from utils.common import get_input,get_formatter,readfile,build_prompt,solve_templates
from utils.client import Client
from utils.formatter import Formatter,PromptBuilder
from utils.executor import StatefulExecutor

def load_command_line():
    if(len(sys.argv) > 1):
        ps = sys.argv[1:]
        fn = ps[0]
        first_prompt = []
        for fn in ps:
            try:
                p=readfile(fn)
                first_prompt.append(p)
            except:
                print("except")
                first_prompt.append(fn)
        return first_prompt
    else:
        return ["{}"]

user_prompt = load_command_line()
client = Client()
client.connect()

parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1
client.set_parameters(parameters)

executor = StatefulExecutor(client)
executor.print_prompt = len(sys.argv) > 1

for i in range(10):
    m = get_input(user_prompt[0],user_prompt[1:])

    executor(m)
    executor.print_prompt = False

    user_prompt = ["{}"]
