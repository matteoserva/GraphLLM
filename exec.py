#!/usr/bin/python3
import sys
from modules.common import get_input,get_formatter,readfile,build_prompt
from modules.clients import Client,DummyClient,GLMClient,ONNXClient
from modules.formatter import Formatter,PromptBuilder

from modules.graph import GraphExecutor
import json

client = Client()
client.connect()

parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1

#test
#parameters["seed"] = 0

executor_config = {"client":client, "client_parameters":parameters}

seqExec = GraphExecutor(executor_config)

cl_args = seqExec.load_config(sys.argv[1:])
res = seqExec(cl_args[1:])
print("\n---------------\nResult:")
res2 = [str(el) for el in res]
print(json.dumps(res2, indent=4))
#for el in res:
#    print(el)
print(res2)

