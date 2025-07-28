from modules.executors.common import BaseGuiNode


class PackGui(BaseGuiNode):
    node_title="Pack"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in","string");
        builder._addInput("2", "string");
        builder._addOutput("out", "string");
        builder._setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 2})
        builder._setPath("other/copy_pack")
        builder._setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

        return builder