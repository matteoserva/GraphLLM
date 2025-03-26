import json
from modules.executors.common import GenericExecutor

class ToolsListNode(GenericExecutor):
    node_type = "tools_list"

    def __init__(self,*args):
        pass

    def initialize(self):
        pass

    def __call__(self, *args):
        tools = self.properties["tools"]
        self.properties["free_runs"] = 1
        return [tools]