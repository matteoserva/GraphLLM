#!/usr/bin/python3
import sys
from modules.common import get_input,get_formatter,readfile,build_prompt
from modules.clients import Client,DummyClient,GLMClient,ONNXClient
from modules.formatter import Formatter,PromptBuilder

from modules.graph import GraphExecutor
import json
from modules.logging.logger import Logger

client = Client()
client.connect()

parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1

logger= Logger()

executor_config = {"client":client, "client_parameters":parameters,"logger":logger}

seqExec = GraphExecutor(executor_config)

try:
    cl_args = seqExec.load_config(sys.argv[1:])
    res = seqExec(cl_args[1:])
    print("\n---------------\nResult:")
    res2 = [str(el) for el in res]
    #print(json.dumps(res2, indent=4))
    for el in res:
        print(el)
    print(res2)
finally:
    logger.stop()