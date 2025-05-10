from modules.executors.common import GenericExecutor

class ImageNode(GenericExecutor):
    node_type = "image_input"

    def __init__(self, node_graph_parameters):
        self.image = {}

    def initialize(self):
        pass

    def graph_started(self):
        variables = self.node.graph.variables
        variables[self.name] = self.image

    def set_parameters(self, conf, **kwargs):
        self.image = conf["image"]
        self.name = conf["name"]

    def __call__(self, prompt_args):
        res = ["{i:" + self.name + "}"]
        return res