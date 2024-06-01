import yaml
import copy

def parse_executor_graph(instructions_raw,cl_args):
    instruction_rows = yaml.safe_load(instructions_raw)
    instruction_flat = []
    for i,v in enumerate(cl_args,1):
        input_obj = {"name": "_C[" + str(i)+"]", "type":"command_line", "conf":i,"init":cl_args[i-1]}
        instruction_flat.append(input_obj)
    instruction_flat.extend(instruction_rows.values())

    for el in instruction_flat:
        if "type" not in el:
            el["type"] = "stateless"
        if "exec" not in el:
            el["exec"] = []
    for el in instruction_rows:
        instruction_rows[el]["name"] = el

    # replace {} with cl_args
    ins_temp = [el for el in instruction_rows.values() if "init" in el]
    graph_temp = "\n".join([el["init"] for el in ins_temp])
    for el in cl_args:
        graph_temp.replace("{}", el, 1)
    graph_temp = graph_temp.split("\n")
    for i, el in enumerate(ins_temp):
        ins_temp[i]["init"] = graph_temp[i]

    # make arrays
    for el in instruction_rows.values():
        for name in ["init","exec"]:
            if name in el:
                if isinstance(el[name], str):
                    val_raw = el[name]
                    val_split =  val_raw.split(" ")
                    val_split = [el.strip() for el in val_split]
                    val_split = [el for el in val_split if len(el) > 0]
                    el[name] = val_split
                elif isinstance(el[name],dict):
                    val = list(el[name].keys())
                    el[name] = "{" + str(val[0])+"}"
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
        farray = [[]]* num_outs
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



