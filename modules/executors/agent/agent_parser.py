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
            node_llm = [el for el in new_nodes if len(new_nodes[el].get("exec",[])) > 0 and new_nodes[el]["type"] == "stateless" and new_nodes[el]["exec"][0]  == agent_name+"[1]"]
            node_tool = [el for el in new_nodes if len(new_nodes[el].get("exec", [])) > 0 and new_nodes[el]["type"] == "tool" and new_nodes[el]["exec"][0] == agent_name + "[2]"]
            node_reflexion = [el for el in new_nodes if len(new_nodes[el].get("exec", [])) > 0 and new_nodes[el]["type"] == "stateless" and new_nodes[el]["exec"][0] == agent_name + "[3]"]
            deps = agent["exec"]
            deps.append(node_llm[0] + "[0]")
            deps.append(node_tool[0] + "[0]")
            if(len(node_reflexion) > 0):
                deps.append(node_reflexion[0] + "[0]")