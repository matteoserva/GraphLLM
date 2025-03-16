from modules.executors.common import BaseGuiNode


class ParseToolCallGui(BaseGuiNode):
    node_title = "Tool Call parser"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in", "string");
        builder._addOutput("out", "string");
        builder._addOutput("json", "string");

        builder._setPath("agent/tool_call_parser")