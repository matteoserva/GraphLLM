from modules.executors.common import BaseGuiParser

class WebsocketsNode(BaseGuiParser):
    node_types = ["websocket_client"]

    def parse_node(self, old_config):
        print(old_config)
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]
        properties = old_config.get("properties", {})
        address = properties.get("address", "")
        
        outputs = [el for el in old_config["outputs"] if "links" in el and el["links"]]
        enable_receive = len(outputs) > 0
        new_config["conf"] = {"address": address, "enable_receive": enable_receive}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        
        print(new_config)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass