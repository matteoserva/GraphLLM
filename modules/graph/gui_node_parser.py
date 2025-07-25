import yaml
from modules.executors import get_gui_parsers
import inspect

class GuiNodeParser:

    def __init__(self):
        self.parsers_list = get_gui_parsers()
        self.parsers_list = [el() for el in self.parsers_list]
        parsers_map = {}
        for el in self.parsers_list:
            for t in el.node_types:
                parsers_map[t] = el
        self.parsers_map = parsers_map
        

    def parse_generic(self ,old_config ,links):
        new_config = {}
        new_config["type"] = old_config["type"]
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", {})
        parameters = yaml.safe_load(parameters)

        for i, el in enumerate(parameters.get("init" ,[])):
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
        new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
        new_inputs = [links[el] if el else None for el in new_inputs]
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        new_config["exec"] = val_exec
        return new_config

    def _calc_exec(self ,old_inputs ,links):

        new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
        new_inputs = [links[el] if el else None for el in new_inputs]
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        return val_exec

    def parse_connection(self ,old_config ,links):
        new_config = {}
        new_config["type"] = "copy"
        new_config["conf"] = {"subtype" :"input"}
        properties = old_config.get("properties", {})
        subtype = properties.get("subtype", "input")
        if subtype == "output":
            new_config["conf"]["subtype"] = "output"

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs ,links)
        return new_config


    def parse_variable(self ,old_config ,links):
        new_config = {}
        new_config["type"] = "variable"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", "")

        new_config["conf"] = {"name" :properties["identifier"] ,"value" :properties["parameters"]}

        old_inputs = old_config.get("inputs", [])
        new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
        new_inputs = [links[el] if el else None for el in new_inputs]
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        new_config["exec"] = val_exec
        return new_config

    def parse_node(self ,old_config ,links):

        new_config = {}
        new_config["type"] = old_config["type"]
        node_type = old_config["type"].split("/")[-1]
        
        if node_type in self.parsers_map:
            old_inputs = old_config.get("inputs", [])
            new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
            new_inputs = [links[el] if el else None for el in new_inputs]
            old_config["inputs"] = new_inputs



            parser_args = {"old_config": old_config, "frontend_config": old_config, "backend_config": {}}
            parser_node = self.parsers_map[node_type]
            parser_function = parser_node.parse_node

            parser_args["backend_config"] = parser_node._make_default_config(old_config)

            sig = inspect.signature(parser_function)
            filter_keys = [param.name for param in sig.parameters.values() if param.kind == param.POSITIONAL_OR_KEYWORD]
            parser_args = {filter_key: parser_args[filter_key] for filter_key in filter_keys}

            res = parser_function(**parser_args)
            
            return res
        if node_type in ["generic_node"]:
            return self.parse_generic(old_config ,links)

        if node_type in ["variable"]:
            return self.parse_variable(old_config, links)
        if node_type in ["connection"]:
            return self.parse_connection(old_config ,links)

        return None

    def postprocess_nodes(self,new_nodes):

        for el in self.parsers_list:
            el.postprocess_nodes(new_nodes)


