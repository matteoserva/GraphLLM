from modules.executors.common import BaseGuiParser


class AgentHistoryBuilderParser(BaseGuiParser):
    node_types = ["agent_history_builder"]



    def parse_node(self, old_config):
        # print(old_config)
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]

        properties = old_config.get("properties", {})
        template = properties.get("template", "")
        new_config["init"] = [template]
        new_config["conf"] = {"agent_type": properties.get("agent_type", ""), "tools_format":properties.get("tools_format", "")}


        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        # print(new_config)
        return new_config