from modules.executors.common import BaseGuiParser


class WebScraperNode(BaseGuiParser):
    node_types = ["web_scraper"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "exec"

        properties = old_config.get("properties", {})
        address = properties.get("address")
        new_config["init"] = ["python3", "extras/scraper/scrape.py", address]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
