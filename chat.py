#!/usr/bin/python3
import sys
from utils.common import get_input,get_formatter,readfile,build_prompt,solve_templates
from utils.client import Client
from utils.formatter import Formatter,PromptBuilder
from utils.executor import StatefulExecutor, StatelessExecutor

client = Client()
client.connect()

parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1

executor = StatefulExecutor(client)
executor.set_client_parameters(parameters)
executor.print_prompt = len(sys.argv) > 1
executor.load_config(sys.argv[1:])

for i in range(10):
    prompt_len = executor.get_prompt_len()

    m = [get_input() for _ in range(prompt_len)]

    executor(m)
    executor.print_prompt = False

