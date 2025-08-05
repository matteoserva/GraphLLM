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

    def parse_node(self ,old_config ,links):

        new_config = {}
        new_config["type"] = old_config["type"]
        node_type = old_config["type"].split("/")[-1]

        res = []
        if node_type in self.parsers_map:
            old_inputs = old_config.get("inputs", [])
            new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
            new_inputs = [links[el] if el else None for el in new_inputs]
            old_config["inputs"] = new_inputs

            parser_args = {"old_config": old_config, "frontend_config": old_config, "backend_config": {}}
            parser_node = self.parsers_map[node_type]
            parser_function = parser_node.parse_node

            backend_config = parser_node._make_default_config(old_config)
            parser_args["backend_config"] = backend_config

            sig = inspect.signature(parser_function)
            filter_keys = [param.name for param in sig.parameters.values() if param.kind == param.POSITIONAL_OR_KEYWORD]
            parser_args = {filter_key: parser_args[filter_key] for filter_key in filter_keys}

            res = parser_function(**parser_args)

            if not res:
                res = []
            elif not isinstance(res,list):
                res = [res]

            if len(res) > 0:
                res[-1]["id"] = str(old_config["id"])

            for i, new_node in enumerate(res[:-1]):
                new_node["id"] = str(old_config["id"]) + "/" + str(i)


        return res

    def postprocess_nodes(self,new_nodes):

        for el in self.parsers_list:
            el.postprocess_nodes(new_nodes)


