from modules.executors.common import BaseGuiParser


class SubgraphParser(BaseGuiParser):
    node_types = ["call_subgraph"]

    def parse_node(self, old_config):
        # print(old_config)
        new_config = {}
        new_config["type"] = "graph"

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        subgraph_name = old_config["properties"]["subgraph_name"]
        new_config["init"] = "json_graphs/" + subgraph_name + ".json"

        return new_config