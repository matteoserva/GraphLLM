from modules.executors.common import BaseGuiNode


class RepeatGui(BaseGuiNode):
    node_title="Repeat"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in","string");
        builder._addOutput("out", "string");
        builder._setPath("repeat")
        options = {"min": 0, "step": 10, "precision": 0, "property": "repetitions"}
        builder._addStandardWidget("number", "repetitions", 0, None, options)
