from modules.executors.common import BaseGuiParser

class LLMParser(BaseGuiParser):
    node_types = ["input"]

    def parse_node(self ,old_config):
        new_config = {}
        new_config["type"] = "constant"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", "")
        new_config["init"] = [parameters]

        new_config["exec"] = []
        return new_config