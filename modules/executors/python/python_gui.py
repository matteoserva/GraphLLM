from modules.executors.common import BaseGuiNode

class PythonNode(BaseGuiNode):
    node_title = "Python"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        builder.addCustomWidget("textarea","Parameters",{ "property": "parameters"})
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")
        builder.setPath("python_sandbox")

        return builder
