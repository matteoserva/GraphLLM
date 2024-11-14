from modules.executors.common import BaseGuiParser
import yaml

class FileParserNode(BaseGuiParser):
    node_types = ["file"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "file"
        properties = old_config.get("properties", {})
        template = properties.get("filename", "")
        new_config["init"] = [template]
        conf = properties.get("config", "")
        conf = yaml.safe_load(conf)
        if conf:
            new_config["conf"] = conf

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
