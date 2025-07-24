from modules.executors.common import BaseGuiParser

class SimpleParser(BaseGuiParser):
    node_types = ["simple_gui"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "simple_node"

        # read the widget values
        properties = old_config.get("properties", {})
        textarea_value = properties.get("textarea_identifier", "")
        new_config["init"] = [textarea_value]

        # define the input nodes
        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

