from . import graph_utils
from .common import readfile,merge_params,try_solve_files
from utils.executor import *

class GraphNode:
    def __init__(self,graph,node_config):
        self.graph = graph
        node = {}
        el = node_config
        if el["type"] == "stateless":
            ex_args = el["exec"]
            self.executor = StatelessExecutor(graph.client)
            if "init" in el:
                init_args = el["init"]
                for i, v in enumerate(init_args):
                    init_args[i], _ = solve_templates(init_args[i], [], graph.variables)
                self.executor.load_config(el["init"])
            executor_parameters = graph.client_parameters
            if "conf" in el and "grammar" in el["conf"]:
                grammarfile = el["conf"]["grammar"]
                grammar = load_grammar(grammarfile)
                new_obj = {grammar["format"]: grammar["schema"]}
                executor_parameters = merge_params(executor_parameters, new_obj)
                pass

            self.executor.set_client_parameters(executor_parameters)
        elif el["type"] == "command_line":
            val = el["init"]

            def dummy_return(d):
                return val
            r = dummy_return
            self.executor = r
            pass

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self,key,value)

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
        input_obj = {"name": "_C", "type": "command_line", "conf": i, "init": cl_args}
        graph_raw.insert(0,input_obj)

        node_connections = graph_utils.create_arcs(graph_raw)
        node_configs = graph_raw


        graph_nodes = []
        for el in node_configs:
            node = GraphNode(self,el)
            graph_nodes.append(node)


        for i,el in enumerate(node_connections):
            num_inputs = len(el["deps"])
            num_outputs = len(el["forwards"])
            graph_nodes[i]["inputs"] = [None] * num_inputs
            graph_nodes[i]["outputs"] = [None] * num_outputs

        self.graph_nodes = graph_nodes
        self.node_configs = node_configs
        self.node_connections = node_connections
        return cl_args

    def _execute_node(self,node_index):
        node = self.graph_nodes[node_index]
        config = self.node_configs[node_index]
        inputs = node["inputs"]

#        m,_ = solve_templates(inputs[0],inputs[1:],self.variables)
        ex = node["executor"]
        res = ex(inputs)
        if not isinstance(res,list):
            res = [res]

        #consuma gli input
        if len(inputs) > 0:
            node["inputs"] = [None] * len(inputs)
        else:
            node["inputs"] = [None]

        #salva gli output
        for i,el in enumerate(res):
            if i < len(node["outputs"]):
                node["outputs"][i] = el
        return res

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
            runnable = [i for i in range(len(self.graph_nodes)) if self._is_runnable(i)]
            if len(runnable) == 0:
                break
            for i in runnable:
                res = self._execute_node(i)
                config = self.node_configs[i]
                name = config["name"]
                rname = "r" + name
                self.variables[rname] = res
                self.variables["r"][name] = res
            self._execute_arcs()
        return res