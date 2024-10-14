import json
import yaml

class JsonParser():
    def __init__(self):
        pass

    def parse_generic(self,old_config,links):
        new_config = {}
        new_config["type"] = old_config["type"]
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", {})
        parameters = yaml.safe_load(parameters)

        for i, el in enumerate(parameters.get("init",[])):
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

    def _calc_exec(self,old_inputs,links):

        new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
        new_inputs = [links[el] if el else None for el in new_inputs]
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        return val_exec


    def parse_llm_call(self,old_config,links):
        new_config = {}
        new_config["type"] = "stateless"
        properties = old_config.get("properties", {})
        template = properties.get("template", "")
        conf = properties.get("conf", "")
        conf = yaml.safe_load(conf)
        if conf:
            new_config["conf"] = conf
        new_config["init"] = [template]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs,links)
        return new_config

    def parse_file(self,old_config,links):
        new_config = {}
        new_config["type"] = "file"
        properties = old_config.get("properties", {})
        template = properties.get("filename", "")
        new_config["init"] = [template]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs,links)
        return new_config

    def parse_input(self,old_config,links):
        new_config = {}
        new_config["type"] = "constant"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", "")
        new_config["init"] = [parameters]

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


    def parse_variable(self,old_config,links):
        new_config = {}
        new_config["type"] = "variable"
        properties = old_config.get("properties", {})
        parameters = properties.get("parameters", "")

        new_config["conf"] = {"name":properties["identifier"],"value":properties["parameters"]}

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

    def parse_virtual(self,old_config,links):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]
        properties = old_config.get("properties", {})
        parameters = properties.get("identifier", "")
        new_config["conf"] = {"name":parameters}

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

    def parse_node(self,old_config,links):

        new_config = {}
        new_config["type"] = old_config["type"]
        if old_config["type"] in ["llm/generic_node"]:
            return self.parse_generic(old_config,links)
        if old_config["type"] in ["llm/input"]:
            return self.parse_input(old_config,links)
        if old_config["type"].startswith("llm/virtual_"):
            return self.parse_virtual(old_config,links)
        if old_config["type"].startswith("llm/watch"):
            return None
        if old_config["type"].startswith("llm/variable"):
            return self.parse_variable(old_config,links)
        if old_config["type"].startswith("llm/llm_call"):
            return self.parse_llm_call(old_config,links)
        if old_config["type"].startswith("llm/file"):
            return self.parse_file(old_config,links)

        return None

    def load_string(self,v):
        jval = json.loads(v)

        links = {str(el[0]):el for el in jval["links"]}
        nodes = { str(el["id"]):el for el in jval["nodes"] if el["type"].startswith("llm/")}
        #print(jval)

        new_nodes = {}
        for el in nodes:
                old_config = nodes[el]
                new_config = self.parse_node(old_config,links)
                if new_config:
                    new_nodes[el] = new_config

        virtual_sinks =   [new_nodes[el] for el in new_nodes if new_nodes[el]["type"] == "virtual_sink"]
        virtual_sources = [new_nodes[el] for el in new_nodes if new_nodes[el]["type"] == "virtual_source"]
        for el in virtual_sources:
                identifier = el["conf"]["name"]
                compatible_sinks = [e for e in new_nodes if new_nodes[e]["type"] == "virtual_sink" and new_nodes[e]["conf"]["name"] == identifier]
                el["type"] = "copy"
                el["exec"] = [compatible_sinks[0]]
        
        for el in virtual_sinks:
                el["type"] = "copy"
        

        return new_nodes

    def load(self, filename):
        with open(filename) as f:
            v = f.read()
        return self.load_string(v)

if __name__ == "__main__":
    parser = JsonParser()
    nodes = parser.load("/tmp/graph.json")
    print (nodes)
    print("---")
    res = yaml.dump(nodes, sort_keys=False)
    print(res)
    with open("/tmp/tmp_graph.yaml","w") as f:
        f.write(res)
