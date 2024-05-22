#!/usr/bin/python3
import sys
from utils.common import get_input,get_formatter,readfile,build_prompt
from utils.client import Client
from utils.formatter import Formatter,PromptBuilder

from utils.executor import SequenceExecutor

client = Client()
client.connect()

parameters = {}
parameters["repeat_penalty"] = 1.0
parameters["penalize_nl"] = False
parameters["seed"] = -1

seqExec = SequenceExecutor(client)
seqExec.set_client_parameters(parameters)

cl_args = seqExec.load_config(sys.argv[1:])
seqExec(cl_args[1:])



