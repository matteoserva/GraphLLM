from modules.executors.common import BaseGuiParser


class PythonParserNode(BaseGuiParser):
    node_types = ["python_sandbox"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "python"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", "")
        new_config["init"] = [parameters]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
