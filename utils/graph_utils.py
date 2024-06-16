import yaml
import copy

def get_clean_config(instructions_raw):
    instruction_rows = yaml.safe_load(instructions_raw)
    res = yaml.dump(instruction_rows, sort_keys=False)
    return res

def parse_executor_graph(instructions_raw):
    instruction_rows = yaml.safe_load(instructions_raw)
    instruction_flat = []

    instruction_flat.extend(instruction_rows.values())

    for el in instruction_flat:
        if "type" not in el:
            el["type"] = "stateless"
        if "exec" not in el:
            el["exec"] = []
    for el in instruction_rows:
        instruction_rows[el]["name"] = el

    # make arrays
    for el in instruction_rows.values():
        for name in ["init","exec","deps"]:
            if name in el:
                if isinstance(el[name], str):
                    val_raw = el[name]
                    val_split =  val_raw.split(" ")
                    val_split = [el.strip() for el in val_split]
                    val_split = [el for el in val_split if len(el) > 0]
                    el[name] = val_split
                elif isinstance(el[name],dict):
                    val = list(el[name].keys())
                    el[name] = ["{" + str(val[0])+"}"]
                    pass


    return instruction_flat


def create_arcs(graph_nodes):
    nodes_map = {}

    arcs = []
    for i,el in enumerate(graph_nodes):
        nodes_map[el["name"]] = i

    num_outputs = [0] * len(graph_nodes)

    for i, el in enumerate(graph_nodes):

        if "exec" in el:
            for di,nn in enumerate(el["exec"]):
                spos = nn.find("[")
                if spos > 0:
                    ssi =  nn[:spos]
                    si = nodes_map[ssi]
                    ssp = nn[spos+1:-1]
                    source_node = si
                    source_port = int(ssp)
                else:
                    si = nodes_map[nn]
                    source_node = si
                    source_port = 0
                dest_node = i
                dest_port = di
                if num_outputs[source_node] < (source_port+1):
                    num_outputs[source_node] = (source_port + 1)
                arcs.append((source_node,source_port,dest_node,dest_port))

    graph_connections = []
    for i, _ in enumerate(graph_nodes):
        num_outs = num_outputs[i]
        farray = [[] for _ in range(num_outs)]
        conn = {"forwards": farray, "deps": []}
        graph_connections.append(conn)

    for arc in arcs:
        si = arc[0]
        sp = arc[1]
        di = arc[2]
        dp = arc[3]
        graph_connections[si]["forwards"][sp].append((di,dp))
        graph_connections[di]["deps"].append((si,sp))

    return graph_connections



