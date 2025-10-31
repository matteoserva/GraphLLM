import yaml
from modules.executors.common import BaseGuiParser
     
class LLMParser(BaseGuiParser):
    node_types = ["llm_call"]
    
    def parse_node(self,old_config):
        
        new_config = {}
        new_config["type"] = "stateless"
        properties = old_config.get("properties", {})
        subtype = properties.get("subtype", "stateless")
        if(subtype == "stateful"):
            new_config["type"] = "stateful"
        template = properties.get("template", "")

        conf = properties.get("conf", "{}")
        conf = yaml.safe_load(conf)
        if not conf:
            conf = {}
        extra_conf = properties.get("extra_config", {})
        conf.update(extra_conf)

        new_config["conf"] = conf
        new_config["init"] = [template]
        
        new_inputs = old_config.get("inputs", [])
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        new_config["exec"] = val_exec
        return new_config

    def postprocess_nodes(self,new_nodes):
        pass