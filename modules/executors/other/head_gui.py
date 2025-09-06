from modules.executors.common import BaseGuiNode


class HeadGui(BaseGuiNode):
    """Forwards only the first (Max runs) elements"""
    node_title="Head"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in","string");
        builder.addOutput("out", "string");
        builder.setPath("head")
        options = {"min": 0, "step": 10, "precision": 0, "property": "max_runs"}
        builder.addStandardWidget("number", "Max runs", 0, None, options)

        return builder