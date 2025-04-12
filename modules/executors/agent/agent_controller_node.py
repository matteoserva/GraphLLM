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
            action_names = [el["name"] for el in result["tool_calls"]]
            actions_type_answer = [(i,el) for i, el in enumerate(action_names) if el.startswith("answer")]
            has_answer = len(actions_type_answer)

            if has_answer:
                results = result["result"]
                answer_index = actions_type_answer[0][0]
                answer = results[answer_index]["result"]
                res = [answer]
            else:
                res = [None, copy.deepcopy(self.run_parameters)]
        return res