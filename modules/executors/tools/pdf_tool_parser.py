from modules.executors.common import BaseGuiParser


class PdfToolNode(BaseGuiParser):
    node_types = ["pdf_parser"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "exec"

        properties = old_config.get("properties", {})
        address = properties.get("address")
        new_config["init"] = ["python3", "extras/parse_pdf.py", address]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
