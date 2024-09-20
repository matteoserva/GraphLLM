#!/usr/bin/python3
import sys
from utils.agent_tools import AgentOps
from utils.client import Client
from utils.common import solve_templates
from utils.formatter import PromptBuilder
from utils.executor import StatelessExecutor,AgentController

agent = AgentOps()

fn = "profmpt.txt"
if(len(sys.argv) > 1):
    fn = sys.argv[1]

f = open(fn)
p = f.read()
f.close()

#import json
#import requests



class AgentGraph:
    def __init__(self, client):
        self.agent_node = AgentController(client)
        executor = StatelessExecutor(client)
        self.executor = executor
        self.current_prompt = ""
        params={}
        params["n_predict"] = 128
        params["stop"] = ["Observation:"]
        params["temperature"] = 0.01
        params["seed"] = -1
        params["cache_prompt"] = True
        params["repeat_penalty"] = 1.0
        params["penalize_nl"] = True
        params["top_k"] = 20
        executor.set_client_parameters(params)
        executor.set_param("force_system", True)
        executor.print_response = "partial"
        self.first_run = True

    def load_config(self,args):
        self.agent_node.load_config(args)



    def __call__(self,prompt_args):
        if self.first_run:
            self.first_run = False
            new_prompt = self.agent_node._handle_query(prompt_args[0])
        else:
            new_prompt = self.agent_node._handle_tool_response(prompt_args[0])

        llm_response = self.executor([new_prompt])
        self.executor.print_prompt = False
        respo = self.agent_node._handle_llm_response(llm_response)
        return respo



client = Client()
client.connect()

ops_string = agent.get_formatted_ops()

agentExecutor = AgentGraph(client)

agentExecutor.agent_node.set_dependencies([agent])

agent_args = sys.argv[1:]
agentExecutor.load_config(agent_args)


#import re
def esegui_comando(respo):
    try:
        res = agent(respo)
    except Exception as e:
        res = "Error: " + str(e)
    return str(res)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

risposta=""

for i in range(10):
    respo = agentExecutor([risposta])
    resp = respo["raw"]
    comando,parametri=respo["command"],respo["args"]

    if comando == "answer":
        #print("")
        print(f"{bcolors.WARNING}Risposta: " + parametri + f"{bcolors.ENDC}")
        break;


    risposta = esegui_comando(respo)
    resp2 = "Observation: " + risposta + "\nThought: "
    print(resp2,end="")
    p = p + resp + resp2
    #print("-"+p+"-")

