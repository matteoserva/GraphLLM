from modules.executors.common import GenericExecutor

from modules.executors.common import BaseGuiParser
import json

class ParseToolCallNode(GenericExecutor):
    node_type = "tool_call_parser"
    def __init__(self,node_graph_parameters):
        pass

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

        res = {"type": "json", "role": "assistant", "content": text_content, "tool_calls": calls}
        return res

    def __call__(self,prompt_args):
        llm_output = str(prompt_args[0])
        if "<action>" in llm_output and "</thinking>" in llm_output:
            res = self._parse_xml_react(llm_output)
            res = [None, res]
        elif "<tool_call>" in llm_output and '"arguments"' in llm_output:
            res = self._parse_qwen_tool(llm_output)
            res = [None, res]
        else:
            res = [llm_output]
        return res