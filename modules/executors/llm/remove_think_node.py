from modules.executors.common import GenericExecutor

class RemoveThinkNode(GenericExecutor):
    node_type = "remove_think"
    def __init__(self,node_graph_parameters):
        pass

    def __call__(self,prompt_args):
        res =prompt_args
        text = res[0]
        stripped = text.lstrip("\n ")
        if stripped.startswith("<think>"):
            text = text.split("</think>")[-1].lstrip()

        return [text]
