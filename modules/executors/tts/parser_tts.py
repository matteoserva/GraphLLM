from modules.executors.common import BaseGuiParser


class PythonParserNode(BaseGuiParser):
    node_types = ["tts"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "tts"
        properties = old_config.get("properties", {})
        language = properties.get("language", "it")
        new_config["conf"] = {"lang": language}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
