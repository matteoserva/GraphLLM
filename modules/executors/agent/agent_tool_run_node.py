from modules.executors.common import GenericExecutor, ExecutorOutput
#from modules.agent_tools import AgentOps
from modules.tool_call.tools_factory import ToolsFactory
import json

class AgentToolRunNode(GenericExecutor):
    node_type = "agent_tool_run"
    def __init__(self,node_graph_parameters):
        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tools_list()
        tool_runner = tools_factory.make_tool_runner(tools_list, node_graph_parameters)
        self.ops = tool_runner
        self.properties = {"wrap_input": True}

    def _execute_react(self,tool_call_data):
        data = tool_call_data["action"]
        parameters = [el["value"] for el in data["parameters"]]
        result = self.ops.exec(data["name"], parameters)
        return result

    def _execute_json(self, tool_call_data):
        tool_calls = tool_call_data["tool_calls"]
        result = []
        for data in tool_calls:
            parameters = [data["arguments"][el] for el in data["arguments"]]
            r = self.ops.exec(data["name"], parameters)
            r = {"result": r}
            result.append(str(r))

        result = ["<tool_response>\n" + json.dumps(el)[1:-1] + "\n</tool_response>" for el in result]
        result = "\n".join(result)
        return result


    def __call__(self,prompt_args):
        wrapped_input = prompt_args[0]

        tool_call_data = wrapped_input.data
        if(tool_call_data["type"] == "react"):
            result = self._execute_react(tool_call_data)
        else:
            result = self._execute_json(tool_call_data)

        tool_call_data["result"] = result
        tool_call_data["content"] = str(result)
        tool_call_data["role"] = "tool"
        outwrapped = ExecutorOutput(tool_call_data)
        if "source_llm" in wrapped_input.meta and tool_call_data["type"] == "native":
            outwrapped.meta["destination"] = (wrapped_input.meta["source_llm"],0)

        res = [result, outwrapped]
        return res