from modules.executors.common import BaseGuiParser

class JsonParser(BaseGuiParser):
    node_types = ["json_parser"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "json_parser"

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass