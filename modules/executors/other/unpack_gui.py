from modules.executors.common import BaseGuiNode


class StandardMuxGui(BaseGuiNode):
    node_title="Unpack"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("vector_in","string");
        builder.addOutput("out", "string");
        builder.setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 1, "max_inputs": 1})
        builder.setPath("other/copy_unpack")

        return builder