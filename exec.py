#!/usr/bin/python3
import sys
from modules.clients import Client, get_client_config
from modules.client_api import TextClientAPI

from modules.graph import GraphExecutor
import json
from modules.client_api.logger import Logger, stop_logger

client_config = get_client_config()
client = Client.make_client(client_config)
client.connect()

def perform_cleaning(message):
    if message.startswith("<think>"):
        message = message.split("</think>",1)[-1].lstrip()
    return message

def run_graph(args,parameters, print_json=False, clean_output=False):
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
        if clean_output:
            res2[0] = perform_cleaning(res2[0])
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
    clean_output = False
    import getopt

    opts, args = getopt.getopt(sys.argv[1:], 'js:k')
    for (k, v) in opts:
        if k == "-j": print_json = True
        if k == "-s": parameters["stop"] = [v]
        if k == "-k": clean_output = True
    run_graph(args,parameters,print_json,clean_output)