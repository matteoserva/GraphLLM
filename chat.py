#!/usr/bin/python3
import sys
from modules.common import get_input,get_formatter,readfile,build_prompt,solve_templates
from modules.clients import Client,GLMClient,GrokClient
from modules.formatter import Formatter,PromptBuilder
from modules.executors import StatefulExecutor, StatelessExecutor
from modules.logging.logger import Logger

client = Client()
client.connect()

logger = Logger()

parameters = {}
#parameters["repeat_penalty"] = 1.0
#parameters["penalize_nl"] = False
parameters["seed"] = -1

#for test
#parameters["seed"] = 0
#parameters["n_probs"] = 5
#parameters["cache_prompt"] = False
parameters["temperature"] = 0.7
#parameters["n_predict"] = 1024*8

executor = StatefulExecutor({"client":client, "logger":logger,"path":"/"})
executor.set_client_parameters(parameters)
executor.print_prompt = len(sys.argv) > 1
executor.load_config(sys.argv[1:])

for i in range(10):
    prompt_len = executor.get_prompt_len()

    m = [get_input() for _ in range(prompt_len)]

    executor(m)
    executor.print_prompt = False

logger.stop()
