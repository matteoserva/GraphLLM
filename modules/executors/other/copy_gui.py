from modules.executors.common import BaseGuiNode

class SimpleCopyGui(BaseGuiNode):
    node_title="Copy"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in","string");
        builder.addOutput("out","string");
        
        builder.setConnectionLimits ({ "min_outputs": 1, "min_inputs": 1})
        builder.setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")
        
        builder.setPath("other/simple_copy")

        return builder