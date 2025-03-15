from modules.executors.common import GenericExecutor

class RemoveThinkNode(GenericExecutor):
    node_type = "remove_think"
    def __init__(self,node_graph_parameters):
        pass

    def __call__(self,prompt_args):
        res =prompt_args
        res[0] = res[0].split("</think>")[-1].lstrip()
        return res
