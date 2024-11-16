from modules.executors.common import BaseGuiParser

class VirtualParser(BaseGuiParser):
    node_types = ["virtual_sink" ,"virtual_source"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]
        properties = old_config.get("properties", {})
        parameters = properties.get("identifier", "")
        new_config["conf"] = {"name" :parameters}

        new_inputs = old_config.get("inputs", [])
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        new_config["exec"] = val_exec
        return new_config


    def postprocess_nodes(self, new_nodes):
        virtual_sinks = [new_nodes[el] for el in new_nodes if new_nodes[el]["type"] == "virtual_sink"]
        virtual_sources = [new_nodes[el] for el in new_nodes if new_nodes[el]["type"] == "virtual_source"]
        for el in virtual_sources:
            identifier = el["conf"]["name"]
            compatible_sinks = [e for e in new_nodes if new_nodes[e]["type"] == "virtual_sink" and new_nodes[e]["conf"]["name"] == identifier]
            el["type"] = "copy"
            el["exec"] = [compatible_sinks[0]]

        for el in virtual_sinks:
            el["type"] = "copy"