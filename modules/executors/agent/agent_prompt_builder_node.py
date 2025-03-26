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
        self.tools_factory = ToolsFactory()
        self.full_tools_list = self.tools_factory.get_tools_list()


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
        res += "<action><action_name>"
        res += data["action"]["name"]
        res += "</action_name>"
        parameters = data["action"]["parameters"]
        for el in parameters:
            res += "<action_parameter name=\""
            res += el["name"]
            res += "\">"
            res += el["value"]
            res += "</action_parameter>"
        res += "</action>\n"
        res += "<result>"
        res += str(data["result"])
        res += "</result>"
        return res

    def __call__(self,prompt_args):
        agent_variables = prompt_args[0] if len(prompt_args) > 0 else {}
        tools_list = prompt_args[1] if len(prompt_args) > 1 else self.full_tools_list
        prompt_subs = prompt_args[2:]

        history = agent_variables.get("history",[])
        res = [self._format_xml_action(data) for data in history]
        agent_variables["history"] = "\n".join(res)
        if len(history) == 0:
            agent_variables["history"] = "<!-- no action performed yet -->"

        tool_runner = self.tools_factory.make_tool_runner(tools_list, {})
        formatted_ops = tool_runner.get_formatted_ops()
        agent_variables["tools"] = formatted_ops

        m = solve_prompt_args(self.current_prompt, prompt_subs)
        m = solve_placeholders(m,[],agent_variables)
        self.builder.reset()
        self.builder.add_request(m)

        res = [m,self.builder.to_string("graphllm"),agent_variables]
        return res
