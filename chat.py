#!/usr/bin/python3
import sys

parameters = {}
#parameters["repeat_penalty"] = 1.0
#parameters["penalize_nl"] = False
parameters["seed"] = -1

#for test
#parameters["seed"] = 0
#parameters["n_probs"] = 5
#parameters["cache_prompt"] = False
parameters["temperature"] = 0.7
#parameters["n_predict"] = 1024*8

from exec import run_graph
args = ["graphs/chat.txt"] + sys.argv[1:]
run_graph(args,parameters)

