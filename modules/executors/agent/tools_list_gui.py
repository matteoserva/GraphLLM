from modules.executors.common import BaseGuiNode


class ToolsListGui(BaseGuiNode):
    node_title = "Tools list"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addOutput("tools", "string");

        builder._addStandardWidget("toggle","math", False, None, {"property":"math", "on": "enabled", "off":"disabled"} )

        builder._setPath("tools_list")