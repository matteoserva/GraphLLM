from modules.executors.common import BaseGuiParser
import yaml

class GenericParser(BaseGuiParser):
    node_types = ["generic_node"]

    def parse_generic(self, old_config):
        new_config = {}
        new_config["type"] = old_config["type"]
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