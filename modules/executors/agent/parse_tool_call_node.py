from modules.executors.common import GenericExecutor

from modules.executors.common import BaseGuiParser

class ParseToolCallNode(GenericExecutor):
    node_type = "tool_call_parser"
    def __init__(self,node_graph_parameters):
        pass

    def _parse_xml_action(self,llm_output):
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
        res = {"planning": "", "thought": thinking, "text": original, "action": action_parsed}
        return res

    def __call__(self,prompt_args):
        llm_output = str(prompt_args[0])
        if "<action>" in llm_output and "</thinking>" in llm_output:
            res = self._parse_xml_action(llm_output)
            res = [None, res]
        else:
            res = [llm_output]
        return res