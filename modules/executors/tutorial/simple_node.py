from modules.executors.common import GenericExecutor

class SimpleNode(GenericExecutor):
    node_type = "simple_node"

    def __init__(self, initial_parameters, *args):
        super().__init__(initial_parameters)

    def initialize(self):
        pass

    # this is the value of the init configuration parameter
    def set_template(self, args):
        self.parameters = args

    def __call__(self, inputs, *args):
        output0 = inputs[0] + self.parameters[0]
        outputs = [output0]
        return outputs