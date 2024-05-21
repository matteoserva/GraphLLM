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

class SequenceExecutor:
    def __init__(self,client):
        #builder = PromptBuilder()
        #builder.load_model(client.get_model_name())
        #self.builder=builder
        self.client = client
        self.execRow = StatelessExecutor(client)

    def load_config(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass
        for el in cl_args[1:]:
            cl_args[0].replace("{}",el,1)
        return cl_args

seqExec = SequenceExecutor(client)
execRow = seqExec.execRow

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

def execute_list(instructions, cl_args):
    pos = 1
    variables={}
    for i,v in enumerate(cl_args):
        idx = i+1
        stri = "c" + str(idx)
        variables[stri] = v
    for instr in instructions:
        res = execute_row(instr,variables)
        fn = "/tmp/llm_exec_" + str(pos) + ".txt"
        f = open(fn,"w")
        f.write(res)
        f.close()
        variables[str(pos)] = res
        pos = pos + 1


cl_args = seqExec.load_config(sys.argv[1:])
lista_istruzioni = cl_args[0]

instructions = [ [ es  for es in el.strip().split(" ") if len(es) > 0] for el in lista_istruzioni.strip().split("\n")]

execute_list(instructions, cl_args[1:])


