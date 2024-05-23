#!/usr/bin/python3
import sys
from utils import agent_ops
from utils.client import Client
from utils.common import solve_templates
from utils.formatter import PromptBuilder
from utils.executor import StatelessExecutor

agent = agent_ops.AgentOps()

fn = "profmpt.txt"
if(len(sys.argv) > 1):
    fn = sys.argv[1]

f = open(fn)
p = f.read()
f.close()

#import json
#import requests

params={}
params["n_predict"] = 128
params["stop"] = ["Observation:"]
params["temperature"] = 0.01
params["seed"] = -1
params["cache_prompt"] = True
params["repeat_penalty"] = 1.0
params["penalize_nl"] = True

client = Client()
client.connect()

ops_string = agent.get_formatted_ops()

executor = StatelessExecutor(client)
executor.set_client_parameters(params)
executor.load_config(["{}{}"] + sys.argv[1:]+[ops_string])
executor.builder.set_param("force_system",True)

#import re
def esegui_comando(istruzione, parametri):
    try:
        res = agent(istruzione,parametri)
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

p=""
executor.print_response="partial"

def clean_response(resp):
    resp = resp.strip()
    while "\n\n" in resp:
       resp = resp.replace("\n\n","\n")
    resp = resp+"\n"
    return resp

for i in range(10):
    resp = executor([p])
    executor.print_prompt=False
#    print(resp,end="")
    resp = clean_response(resp)
    comando = resp[resp.find("Action:")+7:].split("\n")[0].strip()
    if comando.find("(") >= 0: #forma compatta comando(parametri)
        c1 = comando.split("(")
        comando = c1[0].strip()
        parametri = c1[1][:-1]
    else:
        parametri = resp[resp.find("Inputs:")+7:].strip()

#    print(resp,end="")
    if comando == "answer":
        #print("")
        print(f"{bcolors.WARNING}Risposta: " + parametri + f"{bcolors.ENDC}")
        break;

    if resp.find("Answer:")>= 0:
        print("")
        risposta = resp[resp.find("Answer:")+7:].strip().split("\n")[0]
        print(f"{bcolors.WARNING}Risposta: " + risposta + f"{bcolors.ENDC}")
        break
    risposta = esegui_comando(comando,parametri)
    resp2 = "Observation: " + risposta + "\nThought: "
    print(resp2,end="")
    p = p + resp + resp2
    #print("-"+p+"-")

