from modules.executors.common import BaseGuiParser



class CopyParser(BaseGuiParser):
    #node_types = ["standard_mux", "copy_unpack"]

    def parse_node(self, old_config):
        mapping = {}
        mapping["copy_unpack"] = "unpack"
        mapping["standard_mux"] = "mux"

        subtype = old_config["type"].split("/",1)[-1]
        subtype = mapping[subtype]
        new_config = {}
        new_config["type"] = "copy"
        new_config["conf"] = {"subtype" : subtype}

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)
        return new_config


    def postprocess_nodes(self, new_nodes):
        pass