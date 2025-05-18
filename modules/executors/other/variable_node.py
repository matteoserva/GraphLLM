import json
from modules.executors.common import GenericExecutor

class VariableNode(GenericExecutor):
    node_type = "variable"

    def __init__(self,*args):
        pass

    def initialize(self):
        pass

    def set_parameters(self, args):
        self.parameters = args
        conf = self.node.config["conf"]
        graph = self.node.graph
        variables = self.node.graph.variables
        name = conf["name"]
        value = conf["value"]
        if "[" in name:
            name, index = name.split("[",1)
            index = index.split("]")[0]
            if name not in variables:
                variables[name] = {}
            variables[name][index] = value
        else:
            variables[conf["name"]] = conf["value"]

    def __call__(self, *args):
        return []