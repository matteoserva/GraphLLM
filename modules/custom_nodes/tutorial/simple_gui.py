from modules.executors.common import BaseGuiNode

class SimpleGui(BaseGuiNode):
    node_type="simple_gui"

    def buildNode(self):
        builder = self._initBuilder()

        builder.addOutput("out", "string");
        builder.addCustomWidget("textarea", "widget name", {"property": "textarea_identifier"})

        return builder