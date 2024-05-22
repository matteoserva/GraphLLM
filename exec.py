#!/usr/bin/python3
import sys
from utils.common import get_input,get_formatter,readfile,build_prompt
from utils.client import Client
from utils.formatter import Formatter,PromptBuilder

from utils.executor import SequenceExecutor

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


seqExec = SequenceExecutor(client)
execRow = seqExec.execRow
cl_args = seqExec.load_config(sys.argv[1:])
print(cl_args)
seqExec(cl_args[1:])



