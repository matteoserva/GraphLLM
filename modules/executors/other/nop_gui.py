from modules.executors.common import BaseGuiNode


class NopGui(BaseGuiNode):
    """Copies the input to output without waiting for all inputs to be available"""
    node_type = "nop"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        builder.setConnectionLimits({"min_outputs": 1, "min_inputs": 1})
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.mirrorInputs")

        return builder