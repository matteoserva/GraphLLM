from modules.executors.common import BaseGuiParser

class TextInputParser(BaseGuiParser):
    node_types = ["code_infill"]

    def parse_node(self ,old_config):
        new_config = {}
        new_config["type"] = "code_infill"
        properties = old_config.get("properties", {})
        files = properties.get("files", [])
        file_names = [el["name"] for el in files]
        file_init = [el["content"] for el in files]


        new_config["conf"] = {"repo_name": "test", "file_names": file_names}
        new_config["init"] = file_init
        new_config["exec"] = []

        return new_config