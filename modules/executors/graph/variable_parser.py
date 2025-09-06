from modules.executors.common import BaseGuiParser


class VariableParser(BaseGuiParser):
    node_types = ["variable"]


    def parse_node(self ,old_config):
        new_config = {}
        new_config["type"] = "variable"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", "")

        new_config["conf"] = {"name" :properties["identifier"] ,"value" :properties["parameters"]}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config
