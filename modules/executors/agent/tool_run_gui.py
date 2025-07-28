from modules.executors.common import BaseGuiNode


class ParseToolCallGui(BaseGuiNode):
    node_title = "Tool Run"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("result", "string");
        builder.addOutput("tool out", "string");
        builder.addOutput("llm out", "string");

        builder.setPath("execute_tool_call")

        return builder