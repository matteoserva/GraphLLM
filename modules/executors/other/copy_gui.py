from modules.executors.common import BaseGuiNode

class SimpleCopyGui(BaseGuiNode):
    node_title="Copy"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in","string");
        builder._addOutput("out","string");
        
        builder._setConnectionLimits ({ "min_outputs": 1, "min_inputs": 1})
        builder._setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")
        
        builder._setPath("other/simple_copy")

        return builder