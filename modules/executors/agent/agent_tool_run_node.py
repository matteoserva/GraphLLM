from modules.executors.common import GenericExecutor
#from modules.agent_tools import AgentOps
from modules.tool_call.tools_factory import ToolsFactory

class AgentToolRunNode(GenericExecutor):
    node_type = "agent_tool_run"
    def __init__(self,node_graph_parameters):
        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tools_list()
        tool_runner = tools_factory.make_tool_runner(tools_list, node_graph_parameters)
        self.ops = tool_runner


    def __call__(self,prompt_args):

        data = prompt_args[0]["action"]
        parameters = [el["value"] for el in data["parameters"]]
        result = self.ops.exec(data["name"],parameters)
        prompt_args[0]["result"] = result
        res = [result, prompt_args[0]]
        return res