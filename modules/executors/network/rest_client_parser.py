from modules.executors.common import BaseGuiParser

class HttpClientNode(BaseGuiParser):
    node_types = ["rest_client"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]
        properties = old_config.get("properties", {})
        
        url = properties.get("url", "")
        method = properties.get("method", "GET")
        
        new_config["conf"] = {"url": url, "method": method}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        
        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
