from modules.executors.common import BaseGuiNode

class RepeatGui(BaseGuiNode):
    node_title="Simple Gui"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._getBuilder()

        builder._reset()
        builder._addInput("in","string");
        builder._addOutput("out", "string");

        builder._addCustomWidget("textarea", "widget name", {"property": "textarea_identifier"})

        builder._setPath("simple_gui")