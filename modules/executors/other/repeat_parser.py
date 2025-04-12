from modules.executors.common import BaseGuiParser
import ast


class RepeatParser(BaseGuiParser):
    node_types = ["repeat"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "copy"
        rep = old_config["properties"]["repetitions"]
        new_config["conf"] = {"subtype":"repeat", "repeat" : rep}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass