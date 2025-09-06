from modules.executors.common import BaseGuiNode


class RemoveThinkGui(BaseGuiNode):
    node_title = "Remove think"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("llm", "string");
        builder.addOutput("clean text", "string");
        builder.setPath("llm/remove_think")

        return builder