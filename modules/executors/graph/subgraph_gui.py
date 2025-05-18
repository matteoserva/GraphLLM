from modules.executors.common import BaseGuiNode


class SubgraphGui(BaseGuiNode):
    node_title = "Call subgraph"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in", "string");

        builder._addOutput("0ut", "string");

        subgraph_list = []
        builder._addStandardWidget("combo", "graph_name", "<select>", None, {"property": "subgraph_name", "values": subgraph_list})

        builder._setConnectionLimits({"min_outputs": 1, "min_inputs": 1})
        builder._setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

        onNodeAdded = """function(graph) {this.widgets[0].options.values = graph.bridge.graphs_list}"""
        builder._setCallback("onAdded", onNodeAdded)

        builder._setPath("call_subgraph")