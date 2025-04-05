from modules.executors.common import BaseGuiParser


class UDPSenderParser(BaseGuiParser):
    node_types = ["udp_sender"]

    def parse_node(self, old_config):
        new_config = {
            "type": old_config["type"].split("/")[-1],
            "conf": {}
        }
        properties = old_config.get("properties", {})
        new_config["conf"]["ip"] = properties.get("ip", "127.0.0.1")
        new_config["conf"]["port"] = int(properties.get("port", 9999))

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config


class UDPReceiverParser(BaseGuiParser):
    node_types = ["udp_receiver"]

    def parse_node(self, old_config):
        new_config = {
            "type": old_config["type"].split("/")[-1],
            "conf": {}
        }
        properties = old_config.get("properties", {})
        new_config["conf"]["port"] = int(properties.get("port", 9998))
        new_config["conf"]["ip"] = properties.get("ip", "0.0.0.0")
        new_config["conf"]["free_runs"] = properties.get("iterations",1)

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config