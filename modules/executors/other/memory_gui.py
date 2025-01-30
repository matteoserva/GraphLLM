from modules.executors.common import BaseGuiNode


class MemoryGui(BaseGuiNode):
    node_title = "Memory"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in", "string");
        builder._addOutput("out", "string");

        builder._addCustomWidget("text_input", "separator", {"property": "separator","default":"\"\\n\""})
        builder._setPath("other/memory")