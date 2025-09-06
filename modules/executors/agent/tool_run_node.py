from modules.executors.common import GenericExecutor, ExecutorOutput

from modules.executors.common import BaseGuiParser
import json
from modules.tool_call.tools_factory import ToolsFactory

class ParseToolCallNode(GenericExecutor):
    node_type = "execute_tool_call"
    def __init__(self,node_graph_parameters):
        self.properties = {"wrap_input": True}
        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tool_classes(only_default=False)
        tool_runner = tools_factory.make_tool_runner(tools_list, node_graph_parameters)
        self.ops = tool_runner

    def _parse_xml_react(self,llm_output):
        thinking = llm_output.split("</thinking>")[:-1]
        thinking = "</thinking>".join(thinking)
        thinking = thinking.split("<thinking>", 1)[-1]
        thinking = thinking.strip()
        actions = llm_output.split("<action>")[1:]
        actions = [el.split("</action>")[0] for el in actions]
        actions = [el.strip() for el in actions]
        tool_calls = []
        for action in actions:
            action_name = action.split("<action_name>")[-1].split("</action_name>")[0]
            action_parameters = action.split("<action_parameter")[1:]

            action_parameters = [el.split("</action_parameter>", 1)[0] for el in action_parameters]
            action_parameters_parsed = []
            for el in action_parameters:
                parameter_name, parameter_value = el.split(">", 1)
                parameter_name = parameter_name.split("name=",1)[-1][1:-1]
                action_parameters_parsed.append({"name":parameter_name, "value": parameter_value})

            action_parsed = {"name": action_name, "parameters": action_parameters_parsed}
            tool_calls.append(action_parsed)

        original = "<thinking>" + llm_output.split("<thinking>",1)[-1].strip()
        res = {"type": "react", "format": "xml", "planning": "", "thought": thinking, "role": "assistant", "content": original, "tool_calls": tool_calls}
        return res

    def _parse_qwen_tool(self,llm_output):
        calls = llm_output.split("<tool_call>")
        text_content, calls = calls[0], calls[1:]
        calls = [el.split("</tool_call>")[0] for el in calls]
        calls = [el.strip() for el in calls]
        calls = [json.loads(el) for el in calls]
        for call in calls:
            call["parameters"] = [{"name":el, "value":call["arguments"][el]} for el in call["arguments"]]
            del call["arguments"]

        res = {"type": "native", "format": "qwen", "role": "assistant", "content": text_content, "tool_calls": calls}
        return res

    def _execute_react(self,tool_call_data):
        tool_calls = tool_call_data["tool_calls"]
        result = []
        for data in tool_calls:
            parameters = [el["value"] for el in data["parameters"]]
            r = self.ops._exec(data["name"], parameters)
            if not isinstance(r,dict) or "result" not in r:
                r = {"result": r}
            result.append(r)
        return result

    def _execute_json(self, tool_call_data):
        tool_calls = tool_call_data["tool_calls"]
        result = []
        for data in tool_calls:
            parameters = data["parameters"]
            parameters = {el["name"]:el["value"] for el in parameters}
            try:
                r = self.ops._exec(data["name"], **parameters)
            except Exception as w:
                r = w
            if not isinstance(r,dict) or "result" not in r:
                r = {"result": r}
            result.append(str(r))
        return result

    def _execute_tools(self,tool_call_data):
        tool_result = {}
        tool_result["is_final_answer"] = "answer" in [el["name"] for el in tool_call_data["tool_calls"]]

        if (tool_call_data["type"] == "react"):
            response = self._execute_react(tool_call_data)
            response = [el["result"] for el in response]
            loop_response = "\n".join([str(el) for el in response])
            tool_result["response"] = loop_response
            tool_result["loop_data"] = tool_call_data["content"] + "\n" + "<result>" + loop_response + "</result>"
        else:
            result = self._execute_json(tool_call_data)
            response = ["<tool_response>\n" + json.dumps(el)[1:-1] + "\n</tool_response>" for el in result]
            response = "\n".join(response)
            tool_result["response"] = response
            tool_result["loop_data"] = {"role": "tool", "content": str(response)}

        return tool_result

    def _parse_tool_calls(self,wrapped_llm_output):
        llm_output = str(wrapped_llm_output.data)
        tool_call_data = None
        if isinstance(wrapped_llm_output.data, dict) and "type" in wrapped_llm_output.data:
            tool_call_data = wrapped_llm_output.data
        elif "<action>" in llm_output and "</thinking>" in llm_output:
            res = self._parse_xml_react(llm_output)
            tool_call_data = res
        elif "<tool_call>" in llm_output and '"arguments"' in llm_output:
            res = self._parse_qwen_tool(llm_output)
            wrapped_output = res  # ExecutorOutput(res,wrapped_llm_output.meta)
            tool_call_data = wrapped_output
        return tool_call_data

    def __call__(self,prompt_args):
        wrapped_llm_output = prompt_args[0]
        llm_output = str(wrapped_llm_output.data)
        tool_call_data = self._parse_tool_calls(wrapped_llm_output)

        if tool_call_data:
            tool_result = self._execute_tools(tool_call_data)
            outwrapped = ExecutorOutput(tool_result["loop_data"])

            llm_result = None
            if tool_result["is_final_answer"]:
                res = [tool_result["response"], tool_result["response"],None]
            else:
                res = [None, tool_result["response"],outwrapped]

        else:
            res = [llm_output, None, None]
        return res