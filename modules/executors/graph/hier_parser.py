from modules.executors.common import BaseGuiParser


class HierConnectionParser(BaseGuiParser):
    node_types = ["connection"]


    def parse_node(self ,old_config):
        new_config = {}
        new_config["type"] = "copy"
        new_config["conf"] = {"subtype" :"input"}
        properties = old_config.get("properties", {})
        subtype = properties.get("subtype", "input")
        if subtype == "output":
            new_config["conf"]["subtype"] = "output"

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config