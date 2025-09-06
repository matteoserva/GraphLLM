from modules.executors.common import BaseGuiNode


class MemoryGui(BaseGuiNode):
    node_title = "Memory"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        builder.addCustomWidget("text_input", "separator", {"property": "separator","default":"\"\\n\""})
        builder.setPath("other/memory")

        return builder