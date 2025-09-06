from modules.executors.common import BaseGuiNode

class DelayGui(BaseGuiNode):
    node_type="delay"

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");
        options = {"min": 1, "max": 65535, "step": 1, "precision": 2, "property": "delay"}
        builder.addStandardWidget("number", "Delay", 1, None, options)

        return builder