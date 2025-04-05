from modules.executors.common import GenericExecutor
from modules.executors.common import solve_placeholders,solve_prompt_args
from modules.formatter import solve_templates
from modules.formatter import PromptBuilder
from modules.tool_call.tools_factory import ToolsFactory

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

        formatted_ops = self._format_tools_markdown(tools_list)
        agent_variables["tools"] = formatted_ops

        m = solve_prompt_args(self.current_prompt, prompt_subs)
        m = solve_placeholders(m,[],agent_variables)
        self.builder.reset()
        self.builder.add_request(m)

        res = [m,self.builder.to_string("graphllm"),agent_variables]
        return res
