from modules.executors.common import BaseGuiNode


class ParseToolCallGui(BaseGuiNode):
    node_title = "Tool Run"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in", "string");
        builder._addOutput("result", "string");
        builder._addOutput("tool out", "string");
        builder._addOutput("llm out", "string");

        builder._setPath("execute_tool_call")

        return builder