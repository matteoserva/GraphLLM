from modules.executors.common import GenericExecutor
from modules.executors.common import solve_placeholders,solve_prompt_args
from modules.formatter import solve_templates
from modules.formatter import PromptBuilder
from modules.tool_call.tools_factory import ToolsFactory
import json


class AgentHistoryBuilderNode(GenericExecutor):
    node_type = "agent_prompt_builder"
    def __init__(self,node_graph_parameters):
        self.builder = PromptBuilder()
        self.current_prompt = "{}"
        tools_factory = ToolsFactory()
        tool_classes = tools_factory.get_tool_classes()
        self.full_tools_list = tools_factory.get_operators(tool_classes)


    def initialize(self,*args,**kwargs):
        pass
        #self.properties["free_runs"] = 1

    def set_template(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass
        new_prompt, _ = solve_templates(self.current_prompt,cl_args)
        if new_prompt != "":
            self.current_prompt = new_prompt

    def _format_xml_action(self,data):
        res = "<thinking>"
        res += data["thought"]
        res += "</thinking>\n"
        for action in data["tool_calls"]:
            res += "<action><action_name>"
            res += action["name"]
            res += "</action_name>"
            parameters = action["parameters"]
            for el in parameters:
                res += "<action_parameter name=\""
                res += el["name"]
                res += "\">"
                res += el["value"]
                res += "</action_parameter>"
            res += "</action>\n"
        for result in data["result"]:
            res += "<result>"
            res += str(result["result"])
            res += "</result>\n"
        return res

    def _format_tools_markdown(self,tools):
        ops = [el for el in tools]
        textlist = []
        for op in ops:
            row = ""
            row = row + "- " + op["name"]
            if op["doc"] is not None:
                row = row + ": " + op["doc"]
            param_names = [el["name"] for el in op["params"]]
            params_string = ",".join(param_names)
            if row[-1] == ".":
                row = row[:-1]
            row = row + ". Parameters: " + params_string
            textlist.append(row)
        res = "\n".join(textlist)
        return res

    def _format_tools_json(self,tools):
        {"type": "function", "function": {"name": "get_current_temperature", "description": "Get current temperature at a location.", "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "The location to get the temperature for, in the format \"City, State, Country\"."}, "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "The unit to return the temperature in. Defaults to \"celsius\"."}}, "required": ["location"]}}}
        ops = [el for el in tools]
        textlist = []
        for op in ops:
            row = {"type":"function"}
            function = {"name": op["name"]}
            row["function"] = function

            if op["doc"] is not None:
                function["description"] = op["doc"]
            parameters = {"type":"object"}
            function["parameters"] = parameters
            properties = [el["name"] for el in op["params"]]
            parameters["properties"] = properties
            required = [el["name"] for el in op["params"] if el["required"]]
            parameters["required"] = required
            rowstring = json.dumps(row)
            textlist.append(rowstring)
        res = "\n".join(textlist)
        return res

    def _format_tools_python(self,tools):
        ops = [el for el in tools]
        textlist = []
        for op in ops:
            row = ""
            row += "def " + op["name"] + "("
            param_elements = []
            for el in op["params"]:
                param_elem = el["name"]
                if "type" in el:
                    param_elem += ": " + el["type"]
                if not el["required"]:
                    param_elem += " = " + el["default"]
                param_elements.append(param_elem)

            params_string = ", ".join(param_elements)
            row += params_string + ")"
            if "type" in op:
                row += " -> " + op["type"]
            row += ":\n"
            if op["doc"] is not None:
                row += '    """' + op["doc"] + '"""\n'
            textlist.append(row)
        res = "\n".join(textlist)
        return res

    def _format_tools(self,tools,format="markdown"):
        if format == "json":
            res = self._format_tools_json(tools)
        elif format == "python":
            res = self._format_tools_python(tools)
        else:
            res = self._format_tools_markdown(tools)
        return res

    def __call__(self,prompt_args):
        single_shot = len(prompt_args) == 0 or (prompt_args[0] is None and len(prompt_args)< 3) # no controller and no exec
        if single_shot:
            self.node.disable_execution = True
        agent_variables = prompt_args[0] if len(prompt_args) > 0 and prompt_args[0] is not None else {}
        tools_list = prompt_args[1] if len(prompt_args) > 1 and prompt_args[1] is not None else self.full_tools_list
        prompt_subs = prompt_args[2:]

        history = agent_variables.get("history",[])
        res = [self._format_xml_action(data).strip() for data in history]
        history_formatted = "\n".join(res)
        agent_variables["history"] = history_formatted
        if len(history) == 0:
            agent_variables["history"] = "<!-- no action performed yet -->"

        tools_format = self.properties.get("tools_format","markdown")
        formatted_ops = self._format_tools(tools_list,tools_format)
        agent_variables["tools"] = formatted_ops

        m = solve_prompt_args(self.current_prompt, prompt_subs)
        m = solve_placeholders(m,[],agent_variables)
        self.builder.reset()
        self.builder.add_request(m)

        res = [m,self.builder.to_string("graphllm"),agent_variables]
        return res
