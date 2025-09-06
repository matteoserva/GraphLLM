from modules.executors.common import BaseGuiNode


class SubgraphGui(BaseGuiNode):
    node_title = "Call subgraph"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");

        builder.addOutput("0ut", "string");

        subgraph_list = []
        builder.addStandardWidget("combo", "graph_name", "<select>", None, {"property": "subgraph_name", "values": subgraph_list})

        builder.setConnectionLimits({"min_outputs": 1, "min_inputs": 1})
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

        onNodeAdded = """function(graph) {this.widgets[0].options.values = graph.bridge.graphs_list}"""
        builder.setCallback("onAdded", onNodeAdded)

        builder.setPath("call_subgraph")

        return builder