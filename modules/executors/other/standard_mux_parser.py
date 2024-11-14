from modules.executors.common import BaseGuiParser

class CopyParser(BaseGuiParser):
    node_types = ["standard_mux"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "copy"
        new_config["conf"] = {"subtype" : "mux"}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass