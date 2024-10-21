#!/usr/bin/python3
import sys
from modules.common import get_input,get_formatter,readfile,build_prompt,solve_templates
from modules.clients import Client,GLMClient,GrokClient, get_client_config
from modules.formatter import Formatter,PromptBuilder
from modules.executors import StatefulExecutor, StatelessExecutor, ExecutorFactory
from modules.logging.logger import Logger, stop_logger

client_config = get_client_config()
client = Client.make_client(client_config)
client.connect()


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

executor = ExecutorFactory.makeExecutor("stateful",{"client":client})
executor.set_parameters(parameters)
executor.print_prompt = len(sys.argv) > 1
executor.set_template(sys.argv[1:])

try:
    for i in range(100):
        prompt_len = executor.get_prompt_len()

        m = [get_input() for _ in range(prompt_len)]

        executor(m)
        executor.print_prompt = False
except KeyboardInterrupt:
    pass
finally:
    stop_logger()
