from modules.executors.common import BaseGuiNode


class StandardMuxGui(BaseGuiNode):
    node_title="Unpack"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("vector_in","string");
        builder._addOutput("out", "string");
        builder._setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 1, "max_inputs": 1})
        builder._setPath("other/copy_unpack")
