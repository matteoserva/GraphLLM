from modules.executors.common import BaseGuiParser


class ToolsListParser(BaseGuiParser):
    node_types = ["tools_list"]

    def parse_node(self, old_config):
        # print(old_config)
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        tools_dict = old_config["properties"]
        tools_list = [el for el in tools_dict if tools_dict[el]]
        new_config["conf"] = {"tools": tools_list}
        
        return new_config