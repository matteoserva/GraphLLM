from modules.executors.common import BaseGuiParser

class HistoryParser(BaseGuiParser):
    node_types = ["chat_history"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "list"
        properties = old_config.get("properties", {})
        template = properties.get("parameters", [])
        t = ""
        for i, v in enumerate(template):
            if i == 0:
                t += "{p:system}\n" + v + "{p:eom}\n\n"
            elif i % 2:
                t += "{p:user}\n" + v + "{p:eom}\n\n"
            else:
                t += "{p:assistant}\n" + v + "{p:eom}\n\n"

        new_config["init"] = [t]

        new_inputs = old_config.get("inputs", [])
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        new_config["exec"] = []#val_exec
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass