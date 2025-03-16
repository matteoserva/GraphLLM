from modules.executors.common import BaseGuiParser


class AgentToolRunParser(BaseGuiParser):
    node_types = ["agent_tool_run"]

    def parse_node(self, old_config):
        # print(old_config)
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        # print(new_config)
        return new_config