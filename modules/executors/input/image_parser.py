from modules.executors.common import BaseGuiParser


class ImageParser(BaseGuiParser):
    node_types = ["image_input"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]

        properties = old_config.get("properties", {})
        image = properties["image"]
        name = properties.get("name",image["name"])
        new_config["conf"] = {"name": name, "image": image}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config

    def postprocess_nodes(self, new_nodes):
        pass
