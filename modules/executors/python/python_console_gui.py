from modules.executors.common import BaseGuiNode

class PythonConsoleGui(BaseGuiNode):
    node_type="python_console"

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        return builder