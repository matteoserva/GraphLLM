from modules.executors.common import GenericExecutor, ExecutorOutput

from modules.executors.common import BaseGuiParser
import json
from modules.tool_call.tools_factory import ToolsFactory

class ParseToolCallNode(GenericExecutor):
    node_type = "execute_tool_call"
    def __init__(self,node_graph_parameters):
        self.properties = {"wrap_input": True}
        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tools_list(only_default=False)
        tool_runner = tools_factory.make_tool_runner(tools_list, node_graph_parameters)
        self.ops = tool_runner

    def _parse_xml_react(self,llm_output):
        thinking = llm_output.split("</thinking>")[:-1]
        thinking = "</thinking>".join(thinking)
        thinking = thinking.split("<thinking>", 1)[-1]
        thinking = thinking.strip()
        action = llm_output.split("<action>")[-1]
        action = action.split("</action>", 1)[0]
        action = action.strip()
        action_name = action.split("<action_name>")[-1].split("</action_name>")[0]
        action_parameters = action.split("<action_parameter")[1:]

        action_parameters = [el.split("</action_parameter>", 1)[0] for el in action_parameters]
        action_parameters_parsed = []
        for el in action_parameters:
            parameter_name, parameter_value = el.split(">", 1)
            parameter_name = parameter_name.split("name=",1)[-1][1:-1]
            action_parameters_parsed.append({"name":parameter_name, "value": parameter_value})

        action_parsed = {"name": action_name, "parameters": action_parameters_parsed}
        original = "<thinking>" + thinking + "</thinking>\n" + "<action>" + action + "</action>"
        res = {"type": "react", "planning": "", "thought": thinking, "role": "assistant", "content": original, "action": action_parsed}
        return res

    def _parse_qwen_tool(self,llm_output):
        calls = llm_output.split("<tool_call>")
        text_content, calls = calls[0], calls[1:]
        calls = [el.split("</tool_call>")[0] for el in calls]
        calls = [el.strip() for el in calls]
        calls = [json.loads(el) for el in calls]

        res = {"type": "native", "role": "assistant", "content": text_content, "tool_calls": calls}
        return res

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
            r = self.ops.exec(data["name"], **data["arguments"])
            if not isinstance(r,dict):
                r = {"result": r}
            result.append(str(r))

        result = ["<tool_response>\n" + json.dumps(el)[1:-1] + "\n</tool_response>" for el in result]
        result = "\n".join(result)
        return result

    def _execute_tools(self,tool_call_data):
        if (tool_call_data["type"] == "react"):
            result = self._execute_react(tool_call_data)
        else:
            result = self._execute_json(tool_call_data)

        tool_call_data["result"] = result
        tool_call_data["content"] = str(result)
        tool_call_data["role"] = "tool"
        return result

    def __call__(self,prompt_args):
        wrapped_llm_output = prompt_args[0]
        llm_output = str(wrapped_llm_output.data)
        tool_call_data = None
        if isinstance(wrapped_llm_output.data,dict) and "type" in wrapped_llm_output.data:
            tool_call_data = wrapped_llm_output.data
        elif "<action>" in llm_output and "</thinking>" in llm_output:
            res = self._parse_xml_react(llm_output)
            tool_call_data = res
        elif "<tool_call>" in llm_output and '"arguments"' in llm_output:
            res = self._parse_qwen_tool(llm_output)
            wrapped_output = res #ExecutorOutput(res,wrapped_llm_output.meta)
            tool_call_data = wrapped_output
        if tool_call_data:
            tool_result = self._execute_tools(tool_call_data)
            outwrapped = ExecutorOutput(tool_call_data)
            if "source_llm" in wrapped_llm_output.meta and tool_call_data["type"] == "native":
                outwrapped.meta["destination"] = (wrapped_llm_output.meta["source_llm"], 0)
            res = [ outwrapped, tool_result,None]
        else:
            res = [None,None,llm_output]
        return res