from modules.executors.common import GenericExecutor

class AgentHistoryBuilderNode(GenericExecutor):
    node_type = "agent_history_builder"
    def __init__(self,node_graph_parameters):
        pass

    def initialize(self,*args,**kwargs):
        pass
        #self.properties["free_runs"] = 1

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
        agent_variables = prompt_args[0]
        tools_list = prompt_args[1] if len(prompt_args) > 1 else []

        history = agent_variables["history"]

        res = [self._format_xml_action(data) for data in history]
        agent_variables["history"] = "\n".join(res)
        if len(history) == 0:
            agent_variables["history"] = "<!-- no action performed yet -->"
        res = [None,None,agent_variables]
        return res
