from modules.executors.common import GenericExecutor

class SimpleNode(GenericExecutor):
    node_type = "simple_gui"

    def __init__(self, initial_parameters, *args):
        super().__init__(initial_parameters)

    def initialize(self):
        pass

    def __call__(self, inputs, *args):
        textarea_value = self.properties["textarea_identifier"]
        output0 = inputs[0] + textarea_value
        outputs = [output0]
        return outputs