from modules.executors.common import GenericExecutor

class SimpleNode(GenericExecutor):
    node_type = "simple_gui"

    def __call__(self, inputs, *args):
        textarea_value = self.properties["textarea_identifier"]
        output0 = textarea_value
        outputs = [output0]
        return outputs