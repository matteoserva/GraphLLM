from modules.executors.common import BaseGuiNode

class MetronomeGui(BaseGuiNode):
    node_type="metronome"

    def buildNode(self):
        builder = self._initBuilder()

        #builder.addInput("in", "string");
        builder.addOutput("out", "string");
        options = {"min": 1, "max": 65535, "step": 1, "precision": 2, "property": "period"}
        builder.addStandardWidget("number", "Period", 1, None, options)
        builder.addStandardWidget("combo", "Start immediately", "YES", None, {"property": "start_immediate", "values": ["NO", "YES"]})

        return builder