import yaml
import copy

def parse_executor_graph(instructions_raw,cl_args):
    instruction_rows = yaml.safe_load(instructions_raw)
    instruction_flat = []
    for i,v in enumerate(cl_args,1):
        input_obj = {"name": "_C" + str(i), "type":"command_line", "conf":i,"init":cl_args[i-1]}
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



def _parse_arcs(instruction_array):
    arcs = []
    for el in instruction_array:
        if el["type"] != "INS":
            continue
        args = el["clean"].split(" ")

        for arg in args:
            if not arg.startswith("{v:"):
                continue
            val = arg[3:].split("}")[0]
            if val.startswith("c"):
                continue
            if val.startswith("r["):
                val = val[2:-1]
            if val not in el["deps"]:
                el["deps"].append(val)
                arcs.append((val, el["name"]))

            pass

    instruction_rows = {el["name"]: el for el in instruction_array if el["type"] == "INS"}
    for b,f in arcs:
        instruction_rows[b]["forwards"].append(f)


    return instruction_array

def create_arcs(graph_nodes):
    nodes_map = {}
    graph_connections = []
    arcs = []
    for i,el in enumerate(graph_nodes):
        nodes_map[el["name"]] = i
    for i, el in enumerate(graph_nodes):
        conn = {"forwards":[],"deps":[]}
        graph_connections.append(conn)
        if "exec" in el:
            for nn in el["exec"]:
                si = nodes_map[nn]
                arcs.append((si,i))

    for arc in arcs:
        si = arc[0]
        di = arc[1]
        graph_connections[si]["forwards"].append(di)
        graph_connections[di]["deps"].append(si)

    return graph_connections



def load_node_configs(graph_raw):
    graph_temp = [el for el in graph_raw if el["type"] == "INS" or el["type"] == "CONF"]
    for i,el in enumerate(graph_temp):
        if el["type"] == "CONF" and i+1 < len(graph_temp) and graph_temp[i+1]["type"] == "INS":
            graph_temp[i+1]["conf"] = el["clean"]
    graph_nodes = [el for el in graph_raw if el["type"] == "INS"]
    _parse_arcs(graph_nodes)
    return graph_nodes