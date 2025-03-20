from modules.executors.common import GenericExecutor
import copy
from modules.tool_call.tools_factory import ToolsFactory

class AgentToolRunNode(GenericExecutor):
    node_type = "agent_controller"
    def __init__(self,node_graph_parameters):
        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tools_list()
        tool_runner = tools_factory.make_tool_runner(tools_list,node_graph_parameters)
        formatted_ops = tool_runner.get_formatted_ops()
        self.tools = formatted_ops
        self.run_parameters = {}

    def initialize(self):
        self.properties["input_rule"]="OR"

    def __call__(self,prompt_args):
        if prompt_args[0]:
            self.run_parameters = {"tools": self.tools, "question": prompt_args[0], "hints":"", "history": []}
            res = [None, copy.deepcopy(self.run_parameters)]
        else:
            result = prompt_args[1]
            self.run_parameters["history"].append(result)
            action_name = result["action"]["name"]
            if(action_name.startswith("answer")):
                res = [result["result"]]
            else:

                res = [None, copy.deepcopy(self.run_parameters)]
        return res