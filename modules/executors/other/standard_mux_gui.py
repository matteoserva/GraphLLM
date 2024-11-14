from modules.executors.common import BaseGuiNode,GuiNodeBuilder


class StandardMuxGui(BaseGuiNode):
    def __init__(self):
        pass

    def getNodeString(self):
        builder = GuiNodeBuilder()
        builder.addInput("in1","string");
        builder.addInput("in2", "string");
        builder.addOutput("out", "string");
        #builder.addOutput("i", "string");
        builder.setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 2})
        builder.setNames("StandardMuxNode","graph/standard_mux","Mux")
        builder.setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")
        s = builder.generate()
        return s