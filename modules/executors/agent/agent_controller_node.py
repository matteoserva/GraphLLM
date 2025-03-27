from modules.executors.common import GenericExecutor
import copy


class AgentToolRunNode(GenericExecutor):
    node_type = "agent_controller"
    def __init__(self,node_graph_parameters):
        self.run_parameters = {}

    def initialize(self):
        self.properties["input_rule"]="OR"

    def __call__(self,prompt_args):
        if prompt_args[0]:
            self.run_parameters = {"question": prompt_args[0], "hints":"", "history": []}
            res = [None, copy.deepcopy(self.run_parameters)]
        else:
            result = prompt_args[1]
            self.run_parameters["history"].append(result)
            action_name = result["action"]["name"]
            if(action_name.startswith("answer")):
                res = [result["result"]]
            else:

                res = [None, copy.deepcopy(self.run_parameters)]
        return res