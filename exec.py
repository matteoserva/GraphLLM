#!/usr/bin/python3
import sys
from utils.common import get_input,get_formatter,readfile,build_prompt
from utils.client import Client,DummyClient
from utils.formatter import Formatter,PromptBuilder

from utils.graph_executor import GraphExecutor

client = Client()
client.connect()

parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1

executor_config = {"client":client, "client_parameters":parameters}

seqExec = GraphExecutor(executor_config)

cl_args = seqExec.load_config(sys.argv[1:])
res = seqExec(cl_args[1:])
print("Result:", res)



