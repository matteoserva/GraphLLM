from modules.executors.common import BaseGuiParser
import ast


class MemoryParser(BaseGuiParser):
    node_types = ["memory"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "memory"
        sep = old_config["properties"]["separator"]
        try:
            separator = ast.literal_eval(sep)
        except:
            separator = sep
        new_config["conf"] = {"separator" : separator}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass