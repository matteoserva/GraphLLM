from modules.executors.common import GenericExecutor
from modules.agent_tools import AgentOps

class AgentToolRunNode(GenericExecutor):
    node_type = "agent_tool_run"
    def __init__(self,node_graph_parameters):
        self.ops = AgentOps(node_graph_parameters)
        tools_list = ["Filesystem", "LLM", "Util", "Web"]
        self.ops.prepare({"tools":tools_list})

    def __call__(self,prompt_args):

        data = prompt_args[0]["action"]
        parameters = [el["value"] for el in data["parameters"]]
        result = self.ops.exec(data["name"],parameters)
        prompt_args[0]["result"] = result
        res = [result, prompt_args[0]]
        return res