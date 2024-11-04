import json
import yaml
import tempfile
from modules.gui_nodes.llm import GuiNodeParser

class JsonParser():
    def __init__(self):
        pass



    def load_string(self,v):
        jval = json.loads(v)

        links = {str(el[0]):el for el in jval["links"]}
        #valid_sections = ["graph","llm","tools"]

        nodes = { str(el["id"]):el for el in jval["nodes"] if el["type"].split("/")[0]}
        #print(jval)

        gui_node_parser = GuiNodeParser()
        new_nodes = {}
        for el in nodes:
                old_config = nodes[el]
                new_config = gui_node_parser.parse_node(old_config,links)
                if new_config:
                    new_nodes[el] = new_config

        gui_node_parser.postprocess_nodes(new_nodes)

        return new_nodes

    def load(self, filename):
        with open(filename) as f:
            v = f.read()
        return self.load_string(v)

if __name__ == "__main__":
    parser = JsonParser()
    nodes = parser.load(tempfile.gettempdir() + "/graph.json")
    print (nodes)
    print("---")
    res = yaml.dump(nodes, sort_keys=False)
    print(res)
    with open(tempfile.gettempdir() + "/tmp_graph.yaml","w") as f:
        f.write(res)
