#!/usr/bin/python3
import sys
from utils import agent_ops
from utils.client import Client
from utils.common import solve_templates
from utils.formatter import PromptBuilder

agent = agent_ops.AgentOps()

fn = "profmpt.txt"
if(len(sys.argv) > 1):
    fn = sys.argv[1]

f = open(fn)
p = f.read()
f.close()

#host="minipd"



import json
import requests





client = Client()
client.connect()

ops_string = agent.get_formatted_ops()
p,_ = solve_templates(p,[ops_string])
if True:
    builder = PromptBuilder()
    builder.load_model(client.get_model_name())
    builder.add_request(p)
    p = builder._build()
p = client.apply_format_templates(p)
print(p,end="")

import re
def esegui_comando(istruzione, parametri):
    try:
        res = agent(istruzione,parametri)
    except Exception as e:
        res = "Error: " + str(e)
    return str(res)


params={}
params["n_predict"] = 128
params["stop"] = ["Observation:"]
params["temperature"] = 0.01
params["seed"] = -1
params["cache_prompt"] = True
params["repeat_penalty"] = 1.0
params["penalize_nl"] = False
client.set_parameters(params)
#params["top_k"] = 1

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

for i in range(10):
    resp = client.send_prompt(p)
    r2 = "".join(resp)
    resp = r2.strip()
    comando = resp[resp.find("Action:")+7:].split("\n")[0].strip()
    if comando.find("(") >= 0: #forma compatta comando(parametri)
        c1 = comando.split("(")
        comando = c1[0]
        parametri = c1[1][:-1]
    else:
        parametri = resp[resp.find("Inputs:")+7:].strip()

    print(resp,end="")
    if comando == "answer":
        print("")
        print(f"{bcolors.WARNING}Risposta: " + parametri + f"{bcolors.ENDC}")

        break;
    
    if resp.find("Answer:")>= 0:
        print("")
        break
    risposta = esegui_comando(comando,parametri)
    resp2 = "\nObservation: " + risposta + "\nThought: "
    print(resp2,end="")
    p = p + resp + resp2
    #print("-"+p+"-")
    
