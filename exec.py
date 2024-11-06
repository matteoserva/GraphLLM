#!/usr/bin/python3
import sys
from modules.common import get_input,get_formatter,readfile,build_prompt
from modules.clients import Client,DummyClient,GLMClient,ONNXClient, get_client_config
from modules.formatter import Formatter,PromptBuilder
from modules.client_api import TextClientAPI

from modules.graph import GraphExecutor
import json
from modules.logging.logger import Logger, stop_logger

client_config = get_client_config()
client = Client.make_client(client_config)
client.connect()



def run_graph(args,parameters, print_json=False):
    logger = Logger()
    executor_config = {"client": client, "client_parameters": parameters, "logger": logger, "client_api": TextClientAPI()}
    seqExec = GraphExecutor(executor_config)
    try:
        cl_args = seqExec.load_config(args)
        res = seqExec(cl_args[1:])
        print("--------------- Result:")
        res2 = [str(el) for el in res]
        #print(json.dumps(res2, indent=4))
        for el in res:
            print(el)
        if print_json:
            print("--------------- Json result:")
            print(json.dumps(res2))
    except KeyboardInterrupt as e:
        pass
    finally:
        stop_logger()

if __name__ == "__main__":
    parameters = {}
    parameters["repeat_penalty"] = 1.0
    parameters["penalize_nl"] = False
    parameters["seed"] = -1

    print_json = False
    import getopt

    opts, args = getopt.getopt(sys.argv[1:], 'j')
    for (k, v) in opts:
        if k == "-j": print_json = True
    run_graph(args,parameters,print_json)