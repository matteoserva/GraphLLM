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
        tool_classes = self.properties["tools"]
        operators = self.tools_factory.get_operators(tool_classes)
        self.properties["free_runs"] = 1
        return [operators]