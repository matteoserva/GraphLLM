import json
from modules.executors.common import GenericExecutor
from modules.tool_call.tools_factory import ToolsFactory

class ToolsListNode(GenericExecutor):
    node_type = "tools_list"

    def __init__(self,*args):
        self.tools_factory = ToolsFactory()

    def initialize(self):
        pass

    def __call__(self, *args):
        tools_list = self.properties["tools_list"]
        tool_classes = [el for el in tools_list]
        all_operators = self.tools_factory.get_operators(tool_classes)
        selected_operators = [op for cat in tools_list for op in tools_list[cat] if tools_list[cat][op]["enabled"]]

        operators = [el for el in all_operators if el["name"] in selected_operators]
        #self.properties["free_runs"] = 1
        return [operators]