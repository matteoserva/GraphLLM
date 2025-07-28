from modules.executors.common import BaseGuiNode


class StandardMuxGui(BaseGuiNode):
    node_title="Mux"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in1","string");
        builder.addInput("in2", "string");
        builder.addOutput("out", "string");
        builder.addOutput("sel", "string");
        #builder.addOutput("i", "string");
        builder.setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 2})
        builder.setPath("graph/standard_mux")
        builder.setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")

        return builder

class DemuxGui(BaseGuiNode):
    node_title="Demux"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in","string");
        builder.addInput("sel", "string");
        builder.addOutput("out1", "string");
        builder.addOutput("out2", "string");
        #builder.addOutput("i", "string");
        builder.setConnectionLimits ({"max_inputs": 1, "min_inputs": 1, "min_outputs": 2})
        builder.setPath("graph/demux")
        builder.setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")

        return builder