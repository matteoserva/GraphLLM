from modules.executors.common import BaseGuiNode


class RemoveThinkGui(BaseGuiNode):
    node_title = "Remove think"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("llm", "string");
        builder._addOutput("clean text", "string");
        builder._setPath("llm/remove_think")

        return builder