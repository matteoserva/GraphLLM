import yaml
from modules.executors.common import BaseGuiParser

class AgentParser(BaseGuiParser):
    node_types = ["generic_agent"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "agent"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", {})
        parameters = yaml.safe_load(parameters)

        for i, el in enumerate(parameters.get("init", [])):
            if isinstance(el, dict):
                if len(el) > 0:
                    val = list(el.keys())
                    parameters["init"][i] = "{" + str(val[0]) + "}"
                else:
                    parameters["init"][i] = "{}"
                pass

        if parameters:
            for vel in parameters:
                new_config[vel] = parameters[vel]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        agents = [(el, new_nodes[el]) for el in new_nodes if new_nodes[el]["type"] == "agent"]
        for agent_name, agent in agents:
            deps = agent["exec"]
            LLM = deps[1].split("[")[0]
            node = new_nodes[LLM]
            node["exec"] = [agent_name + "[1]"]
            tools = deps[2].split("[")[0]
            node = new_nodes[tools]
            node["exec"] = [agent_name + "[2]"]
            if len(deps) > 3:
                reflex = deps[3].split("[")[0]
                node = new_nodes[reflex]
                node["exec"] = [agent_name + "[3]"]