from modules.executors.common import BaseGuiNode


class JsonGui(BaseGuiNode):
    """
        Parses and indents a json string
    """
    node_title = "JSON parser"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        builder.setPath("json_parser")

        return builder