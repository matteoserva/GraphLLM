from modules.executors.common import BaseGuiParser

class HeadParser(BaseGuiParser):
    node_types = ["head"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "copy"
        rep = old_config["properties"]["max_runs"]
        new_config["conf"] = {"max_runs":rep}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass