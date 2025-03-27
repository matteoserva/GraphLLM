from modules.executors.common import BaseGuiNode
from modules.tool_call.tools_factory import ToolsFactory

class ToolsListGui(BaseGuiNode):
    node_title = "Tools list"

    def __init__(self):
        tools_factory = ToolsFactory()
        self.tools_list = tools_factory.get_tool_classes(only_default=False)

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addOutput("tools", "string");

        for el in self.tools_list:
            builder._addStandardWidget("toggle",el, el == "answer", None, {"property":el, "on": "enabled", "off":"disabled"} )   

        builder._setPath("tools_list")