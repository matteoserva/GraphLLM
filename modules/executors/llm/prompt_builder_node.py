from modules.formatter import PromptBuilder
from modules.executors.common import GenericExecutor
from modules.executors.common import solve_placeholders
from modules.formatter import solve_templates

from modules.executors.common import BaseGuiParser

class PromptBuilderNode(GenericExecutor):
    node_type = "prompt_builder"
    def __init__(self,node_graph_parameters):
        self.current_prompt="{}"
        self.builder = PromptBuilder()
        self.client = node_graph_parameters["client"]

    def initialize(self):
        self.builder.load_model(self.client.get_model_name())

    def set_template(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass
        new_prompt, _ = solve_templates(self.current_prompt,cl_args)
        if new_prompt != "":
            self.current_prompt = new_prompt

    def __call__(self,prompt_args):
        m ,_ = solve_templates(self.current_prompt,prompt_args)
        m = solve_placeholders(m,prompt_args)

        self.builder.reset()
        self.builder.add_request(m)
        prompt = self.builder._build()
        res = [m,prompt,self.builder]

        return res


class PromptBuilderParser(BaseGuiParser):
    node_types = ["prompt_builder"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]
        properties = old_config.get("properties", {})
        template = properties.get("template", "")
        new_config["init"] = [template]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass