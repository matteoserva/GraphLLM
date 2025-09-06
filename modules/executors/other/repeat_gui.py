from modules.executors.common import BaseGuiNode


class RepeatGui(BaseGuiNode):
    node_title="Repeat"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in","string");
        builder.addOutput("out", "string");
        builder.setPath("repeat")
        options = {"min": 0, "step": 10, "precision": 0, "property": "repetitions"}
        builder.addStandardWidget("number", "repetitions", 0, None, options)

        return builder