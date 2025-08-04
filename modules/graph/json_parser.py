import json
import yaml
import tempfile
from modules.graph.gui_node_parser import GuiNodeParser

class JsonParser():
    def __init__(self):
        pass


    def _solve_links(self,nodes,links):
        for node_id in nodes:
            node = nodes[node_id]
            inputs = node.get("inputs",[])
            outputs = node.get("outputs",[])
            new_inputs = [links[str(el["link"])] if el["link"] else None for el in inputs]
            new_inputs = [ nodes[str(el[1])] if el else None for el in new_inputs]
            new_outputs = [el["links"] if el.get("links",None) else [] for el in outputs]
            new_outputs = [ [ links[str(el)]  for el in s ] for s in new_outputs ]
            new_outputs = [ [ nodes[str(el[3])]  for el in s ] for s in new_outputs ]
            node["linked_inputs"] = new_inputs
            node["linked_outputs"] = new_outputs
            pass

    def load_string(self,v):
        jval = json.loads(v)

        links = {str(el[0]):el for el in jval.get("links",[])}
        #valid_sections = ["graph","llm","tools"]

        gui_nodes = { str(el["id"]):el for el in jval.get("nodes",[]) if el["type"].split("/")[0]}
        #print(jval)

        self._solve_links(gui_nodes,links)

        gui_node_parser = GuiNodeParser()
        new_nodes = {}
        for el in gui_nodes:
                old_config = gui_nodes[el]
                new_config = gui_node_parser.parse_node(old_config,links)
                for new_node in new_config:
                    node_id = new_node["id"]
                    del new_node["id"]
                    new_nodes[node_id] = new_node

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
