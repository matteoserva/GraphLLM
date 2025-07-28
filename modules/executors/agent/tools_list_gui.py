from modules.executors.common import BaseGuiNode
from modules.tool_call.tools_factory import ToolsFactory

class ToolsListGui(BaseGuiNode):
    node_title = "Tools list"

    def __init__(self):
        tools_factory = ToolsFactory()
        self.tools_list = tools_factory.get_tool_classes(only_default=False)
        self.operators = {el: tools_factory.get_operators([el]) for el in self.tools_list }


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addOutput("tools", "string");

        #for el in self.tools_list:
        #    builder._addStandardWidget("toggle",el, el == "answer", None, {"property":el, "on": "enabled", "off":"disabled"} )

        tools_list = {}
        for el in self.operators:
            l = self.operators[el]
            l = [el["name"] for el in l]
            tools_list[el] = l

        builder._addCustomWidget("tools_selector", "tools_list", {"property": "tools_list", "tools_list":tools_list})

        builder._setPath("tools_list")

        return builder