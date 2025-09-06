from modules.executors.common import GenericExecutor

class NopNode(GenericExecutor):
    node_type = "nop"

    def initialize(self,*args,**kwargs):
        self.node.set_parameter("input_rule", "OR")

    def __call__(self, inputs, *args):
        outputs = [el for el in inputs]
        return outputs