from . import graph_utils
from .common import readfile,merge_params,try_solve_files
from utils.executor import *



class GraphNode:
    def __init__(self,graph,node_config):
        self.graph = graph
        self.free_runs = 0
        self.disable_execution = False
        self.input_rule="AND"
        self.type = node_config["type"]
        self.name = node_config["name"]
        node = {}
        el = node_config
        if el["type"] == "stateless":
            self.executor = StatelessExecutor(graph.client)

        elif el["type"] == "command_line":
            self.executor = ConstantNode()
        elif el["type"] == "agent":
            self.executor = AgentController()
            self.input_rule = "OR"
        elif el["type"] == "tool":
            self.executor = ToolExecutor()
        elif el["type"] == "copy":
            self.executor = CopyNode()
        elif el["type"] == "graph":
            self.executor = GraphExecutor(graph.client)
            #
    def execute(self):
        node=self
        inputs = node["inputs"]

        #        m,_ = solve_templates(inputs[0],inputs[1:],self.variables)
        ex = node["executor"]
        res = ex(inputs)
        if not isinstance(res, list):
            res = [res]

        # consuma gli input
        if self["free_runs"] > 0:
            self["free_runs"] -= 1
        elif len(inputs) > 0:
            node["inputs"] = [None] * len(inputs)
        else:
            self.disable_execution = True

        # salva gli output
        for i, el in enumerate(res):
            if i < len(node["outputs"]):
                node["outputs"][i] = el

        return res

    def is_runnable(self):
        node = self
        if self["free_runs"]> 0:
            return True
        if self.disable_execution:
            return False

        missing_inputs = len([el for el in node["inputs"] if el is None])
        blocked_outputs = len([el for el in node["outputs"] if not el is None])
        if (self.input_rule == "OR"):
            available_inputs = len([el for el in node["inputs"] if el is not None])
            missing_inputs = 0 if available_inputs > 0 else missing_inputs

        runnable = (missing_inputs + blocked_outputs) == 0
        return runnable

    def set_dependencies(self,deps):
        self.executor.set_dependencies(deps)

    def prepare(self,args):
        if self.type == "graph":
            self.executor.set_client_parameters(self.graph.client_parameters)
        elif args is  None:
            if hasattr(self.executor, "prepare"):
                pass
        elif self.type == "stateless" :
            executor_parameters = self.graph.client_parameters
            self.executor.set_client_parameters(executor_parameters)
            new_obj = {}
            for key in ["stop", "n_predict","temperature","top_k"]:
                if key in args:
                    new_obj[key] = args[key]

            if "grammar" in args:
                grammarfile = args["grammar"]
                grammar = load_grammar(grammarfile)
                new_obj[grammar["format"]] = grammar["schema"]

            executor_parameters = merge_params(executor_parameters, new_obj)
            self.executor.set_client_parameters(executor_parameters)

            for key in ["force_system"]:
                if key in args:
                    self.executor.set_param(key,args[key])
        elif self.type == "copy":
            self.executor.set_parameters(args)
        elif self.type == "tool":
            self.executor.prepare(args)
        else:
            pass

    def load_template(self,init_args):
        for i, v in enumerate(init_args):
            init_args[i], _ = solve_templates(init_args[i], [], self.graph.variables)
        self.executor.load_config(init_args)


    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self,key,value)

def _make_graph_node(graph,node_config):
    node = GraphNode(graph, node_config)
    return node



class GraphExecutor:
    def __init__(self,client):

        #self.execRow = StatelessExecutor(client)
        self.client = client
        self.client_parameters = None
        self.variables={"c": {}, "r":{}}

    def set_client_parameters(self,p):
        self.client_parameters = p
        #self.execRow.set_client_parameters(p)



    def load_config(self,cl_args=None):
        try_solve_files(cl_args)
        for i,v in enumerate(cl_args):
            idx = i
            stri = "c" + str(idx)
            self.variables[stri] = v
            self.variables["c"][str(idx)] = v
        instructions_raw = None

        clean_config = cl_args[0]
        clean_config = graph_utils.get_clean_config(clean_config)
        for i,el in enumerate(cl_args[1:],1):
            rstr = "{v:c["+ str(i) + "]}"
            clean_config = clean_config.replace("{}",rstr,1)
        graph_raw = graph_utils.parse_executor_graph(clean_config)

        #add command_line node
        input_obj = {"name": "_C", "type": "command_line", "init": cl_args}
        graph_raw.insert(0,input_obj)

        node_connections = graph_utils.create_arcs(graph_raw)
        node_configs = graph_raw


        graph_nodes = []
        for el in node_configs:
            node = _make_graph_node(self,el)
            graph_nodes.append(node)

        nodes_map = {el["name"]:el for el in graph_nodes}
        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "deps" in config:
                solved_deps = [nodes_map[el].executor for el in config["deps"]]
                node.set_dependencies(solved_deps)

        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "conf" in config:
                node.prepare(config["conf"])
            else:
                node.prepare(None)

        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "init" in config:
                node.load_template(config["init"])

        for i,el in enumerate(node_connections):
            num_inputs = len(el["deps"])
            num_outputs = len(el["forwards"])
            graph_nodes[i]["inputs"] = [None] * num_inputs
            graph_nodes[i]["outputs"] = [None] * num_outputs

        self.graph_nodes = graph_nodes
        self.node_configs = node_configs
        self.node_connections = node_connections
        return cl_args


    def _is_runnable(self,node_index):
        node = self.graph_nodes[node_index]

        missing_inputs = len([el for el in node["inputs"] if el is None])
        blocked_outputs = len([el for el in node["outputs"] if not el is None])


        runnable = (missing_inputs + blocked_outputs) == 0
        return runnable

    def _execute_arcs(self):
        for node_index,node in enumerate(self.graph_nodes):
            source_outputs = node["outputs"]
            forwards = self.node_connections[node_index]["forwards"]
            for source_port,forwards in enumerate(forwards):
                current_output = source_outputs[source_port]
                destination_inputs = [self.graph_nodes[i]["inputs"][p] for i,p in forwards]
                destination_ready = len([el for el in destination_inputs if el is not None]) == 0
                source_ready = current_output is not None
                if (not source_ready) or (not destination_ready):
                    continue
                for di,dp in forwards:
                    self.graph_nodes[di]["inputs"][dp] = current_output
                node["outputs"][source_port] = None
                pass

    def __call__(self,prompt):
        res = None

        while True:
            runnable = [i for i,v in enumerate(self.graph_nodes) if v.is_runnable()]
            if len(runnable) == 0:
                break
            for i in runnable:
                res = self.graph_nodes[i].execute()
                config = self.node_configs[i]
                name = config["name"]
                rname = "r" + name
                self.variables[rname] = res
                self.variables["r"][name] = res
            self._execute_arcs()
        return res