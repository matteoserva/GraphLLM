from modules.executors.common import BaseGuiParser


class OutputsParserNode(BaseGuiParser):
    node_types = ["watch","html_canvas"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "copy"

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
