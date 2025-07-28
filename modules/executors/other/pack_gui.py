from modules.executors.common import BaseGuiNode


class PackGui(BaseGuiNode):
    node_title="Pack"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in","string");
        builder.addInput("2", "string");
        builder.addOutput("out", "string");
        builder.setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 2})
        builder.setPath("other/copy_pack")
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

        return builder