from modules.executors.common import BaseGuiNode


class StandardMuxGui(BaseGuiNode):
    node_title="Mux"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in1","string");
        builder._addInput("in2", "string");
        builder._addOutput("out", "string");
        builder._addOutput("sel", "string");
        #builder.addOutput("i", "string");
        builder._setConnectionLimits ({"max_outputs": 1, "min_outputs": 1, "min_inputs": 2})
        builder._setPath("graph/standard_mux")
        builder._setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")

        return builder

class DemuxGui(BaseGuiNode):
    node_title="Demux"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in","string");
        builder._addInput("sel", "string");
        builder._addOutput("out1", "string");
        builder._addOutput("out2", "string");
        #builder.addOutput("i", "string");
        builder._setConnectionLimits ({"max_inputs": 1, "min_inputs": 1, "min_outputs": 2})
        builder._setPath("graph/demux")
        builder._setCallback("onConnectionsChange","MyGraphNode.prototype.onConnectionsChange")

        return builder