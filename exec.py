#!/usr/bin/python3
import sys
from utils.common import get_input,get_formatter,readfile,build_prompt
from utils.client import Client
from utils.formatter import Formatter,PromptBuilder
from utils.parser import solve_templates
from utils.executor import StatelessExecutor



fn = "sequences/reddit_eval.txt"
if len(sys.argv) > 1:
    fn = sys.argv[1]

client = Client()
client.connect()


parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1
client.set_parameters(parameters)

execRow = StatelessExecutor(client)

def execute_row(inputs,variables={}):
    for i in range(len(inputs)):
        try:
            p=readfile(inputs[i])
            inputs[i] = p
        except:
            pass
    m,_ = solve_templates(inputs[0],inputs[1:],variables)
    res = execRow(m)

    return res

def execute_list(instructions):
    pos = 1
    variables={}
    for instr in instructions:
        res = execute_row(instr,variables)
        fn = "/tmp/llm_exec_" + str(pos) + ".txt"
        f = open(fn,"w")
        f.write(res)
        f.close()
        variables[str(pos)] = res
        pos = pos + 1


lista_istruzioni = readfile(fn)

for el in sys.argv[2:]:
    lista_istruzioni = lista_istruzioni.replace("{}",el,1)

instructions = [ [ es  for es in el.strip().split(" ") if len(es) > 0] for el in lista_istruzioni.strip().split("\n")]

execute_list(instructions)


