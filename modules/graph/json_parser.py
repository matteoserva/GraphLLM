import json
import yaml

class JsonParser():
    def __init__(self):
        pass

    def load(self,filename):
        with open(filename) as f:
            v = f.read()

        jval = json.loads(v)

        links = {str(el[0]):el for el in jval["links"]}
        nodes = { str(el["id"]):el for el in jval["nodes"] if el["type"].startswith("llm/")}
        print(jval)

        for el in nodes:
                old_config = nodes[el]
                new_config = {}
                new_config["type"] = old_config["type"]
                properties = old_config.get("properties",{})
                parameters = properties.get("parameters","")
                parameters = yaml.safe_load(parameters)
                if parameters:
                   for vel in parameters:
                      new_config[vel] = parameters[vel]
                old_inputs = old_config.get("inputs",[])
                new_inputs = [str(el["link"]) if el["link"] else None for el in old_inputs]
                new_inputs = [links[el] if el else None for el in new_inputs ]
                new_inputs = [ str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs ]
                val_exec = []
                for vel in new_inputs:
                    if not vel:
                       break
                    val_exec.append(vel)
                new_config["exec"] = val_exec

                nodes[el] = new_config
        return nodes

if __name__ == "__main__":
    parser = JsonParser()
    nodes = parser.load("/tmp/graph.json")
    print (nodes)
    print("---")
    res = yaml.dump(nodes, sort_keys=False)
    print(res)
    with open("/tmp/tmp_graph.yaml","w") as f:
        f.write(res)
