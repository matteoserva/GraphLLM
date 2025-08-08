from modules.executors.common import BaseGuiNode

class PythonConsoleGui(BaseGuiNode):
    node_type="python_console"

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        builder.addStandardWidget("combo", "Echo", "YES", None, {"property": "echo", "values": ["NO","YES"]})
        builder.addStandardWidget("combo", "Strip sysPS", "AUTO", None, {"property": "strip", "values": ["NO", "AUTO", "YES"]})
        builder.addStandardWidget("combo", "Stop at Exception", "NO", None, {"property": "stop_exception", "values": ["NO", "YES"]})
        return builder