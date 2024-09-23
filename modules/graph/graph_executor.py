from . import graph_utils
from ..common import readfile,merge_params,try_solve_files
from modules.executors import *

from modules.clients import Client,DummyClient,GLMClient,ONNXClient
from ..grammar import load_grammar
import threading

class GraphNode:
    def __init__(self,graph,node_config):
        self.graph = graph
        self.free_runs = 0
        self.disable_execution = False

        self.type = node_config["type"]
        self.name = node_config["name"]
        node = {}
        el = node_config
        if el["type"] == "stateless":
            self.executor = StatelessExecutor(graph.client)
        elif el["type"] == "stateful":
            self.executor = StatefulExecutor(graph.client)
        elif el["type"] == "constant":
            self.executor = ConstantNode()
        elif el["type"] == "agent":
            self.executor = AgentController()
        elif el["type"] == "tool":
            self.executor = ToolExecutor()
        elif el["type"] == "list":
            self.executor = ListNode()
        elif el["type"] == "copy":
            self.executor = CopyNode()
        elif el["type"] == "graph":
            self.executor = GraphExecutor(graph.client)
        elif el["type"] == "python":
            self.executor = PythonExecutor()
        elif el["type"] == "llamatool":
            self.executor = LlamaTool()
        elif el["type"] == "client":
            self.executor = Client()
        elif el["type"] == "user":
            self.executor = UserInputNode()
        elif el["type"] == "exec":
            self.executor = ExecNode()


    def _get_input_rule(self):
        self.input_rule = "AND"
        props = None
        if hasattr(self.executor, "get_properties"):
            props = self.executor.get_properties()
        elif hasattr(self.executor, "properties"):
            props = self.executor.properties

        if props is not None:
            if "input_rule" in props:
                self.input_rule = props["input_rule"]
            if "free_runs" in props:
                self["free_runs"] = props["free_runs"]
            if "input_active" in props:
                self["input_active"] = props["input_active"]
        return self.input_rule

    def setup_complete(self):
        pass

    def execute(self):
        node=self
        inputs = [el for el in node["inputs"]]

        #        m,_ = solve_templates(inputs[0],inputs[1:],self.variables)
        ex = node["executor"]



        consume_inputs = [True] * len(inputs)

        if self["free_runs"] > 0:
            self["free_runs"] -= 1
            inputs = [""] * len(inputs)
            consume_inputs = [False] * len(inputs)
        elif self.input_rule == "XOR":
            consume_inputs = [False] * len(inputs)
            consume_inputs[self["input_active"]] = True
            inputs = [None] * len(inputs)
            inputs[self["input_active"]] = node["inputs"][self["input_active"]]
        elif self.input_rule == "OR":
            consume_inputs = [False] * len(inputs)
            available_inputs = [ i for i, el in enumerate(node["inputs"]) if el is not None]
            input_active = available_inputs[0]
            consume_inputs[input_active] = True
            inputs = [None] * len(inputs)
            inputs[input_active] = node["inputs"][input_active]
        elif len(inputs) > 0:
            node["inputs"] = [None] * len(inputs)
            consume_inputs = [True] * len(inputs)
        else:
            self.disable_execution = True

        # consuma gli input
        for i, el in enumerate(consume_inputs):
            if el:
                node["inputs"][i] = None

        res = ex(inputs)
        if not isinstance(res, list):
            res = [res]


        # salva gli output
        node["last_output"] = res
        for i, el in enumerate(res):
            if i < len(node["outputs"]):
                node["outputs"][i] = el

        return res

    def is_runnable(self):
        node = self
        input_rule = self._get_input_rule()

        missing_inputs = len([el for el in node["inputs"] if el is None])
        blocked_outputs = len([el for el in node["outputs"] if not el is None])
        if ( input_rule == "OR"):
            available_inputs = len([el for el in node["inputs"] if el is not None])
            missing_inputs = 0 if available_inputs > 0 else missing_inputs
        if ( input_rule == "XOR"):
            input_available = node["inputs"][self["input_active"]] is not None
            missing_inputs = 0 if input_available else 1

        if self["free_runs"]> 0 and blocked_outputs == 0:
            return True
        if self.disable_execution:
            return False
        if len( node["inputs"]) == 0 and len(node["outputs"]) == 0:
            return False

        runnable = (missing_inputs + blocked_outputs) == 0
        return runnable

    def set_dependencies(self,deps):
        r = list(deps.values())
        #print(r)
        if self.type=="stateless" or self.type=="stateful":
            self.executor.set_dependencies(deps)
        else:
            self.executor.set_dependencies(r)

    def set_config(self,args):
        if self.type == "graph":
            self.executor.set_client_parameters(self.graph.client_parameters)
        elif args is None:
            if hasattr(self.executor, "prepare"):
                pass
        elif self.type == "stateless" or self.type == "stateful" :
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

            for key in ["force_system","print_prompt","sysprompt"]:
                if key in args:
                    self.executor.set_param(key,args[key])
        elif self.type == "copy":
            self.executor.set_parameters(args)
        elif self.type == "tool":
            self.executor.prepare(args)
        elif self.type == "agent":
            self.executor.set_parameters(args)
        elif self.type == "client":
            self.executor.set_parameters(args)
        elif hasattr(self.executor, "set_parameters"):
            self.executor.set_parameters(args)
        elif isinstance(args,dict):
            for el in args:
                setattr(self.executor,el,args[el])
        else:
            pass

    def set_template(self,init_args):
        new_init_args = []
        for i, v in enumerate(init_args):
            if v == "{v:c*}":
                new_init_args.extend(self.graph.variables["c*"])
            else:
                new_init_args.append(v)
        init_args = new_init_args
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
    def __init__(self,executor_config):
        if not isinstance(executor_config, dict):
            executor_config = {"client":executor_config}

        client = executor_config["client"]
        if "client_parameters" in executor_config:
            self.client_parameters = executor_config["client_parameters"]
        else:
            self.client_parameters = None

        self.client = client
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
        self.variables["c*"] = cl_args[1:]
        self.variables["current_date"] = "23 Jul 2024"
        instructions_raw = None

        clean_config = cl_args[0]
        clean_config = graph_utils.get_clean_config(clean_config)

        for i,el in enumerate(cl_args[1:],1):
            rstr = "{v:c["+ str(i) + "]}"
            clean_config = clean_config.replace("{}",rstr,1)

        #variable_whitelist = ["current_date"]
        #whitelisted_variables = {name:self.variables[name] for name in variable_whitelist if name in self.variables}
        #clean_config, _ = solve_templates(clean_config, [], whitelisted_variables)
        clean_config = clean_config.replace("{v:current_date}",self.variables["current_date"])
        graph_raw = graph_utils.parse_executor_graph(clean_config)

        #add output node if there is only one node
        if len(graph_raw) == 1:
            obj = {"name": "_O", "type": "copy","exec":[graph_raw[0]["name"]]}
            graph_raw.append(obj)

        #add command_line node
        input_obj = {"name": "_C", "type": "constant", "init": cl_args}
        graph_raw.insert(0,input_obj)

        #add input node
        input_obj = {"name": "_I", "type": "copy"}
        graph_raw.insert(0, input_obj)

        node_connections = graph_utils.create_arcs(graph_raw)
        node_configs = graph_raw


        graph_nodes = []
        for el in node_configs:
            node = _make_graph_node(self,el)
            graph_nodes.append(node)

        nodes_map = {el["name"]:el for el in graph_nodes}


        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "conf" in config:
                node.set_config(config["conf"])
            else:
                node.set_config(None)

        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "deps" in config:
                solved_deps = {el:nodes_map[config["deps"][el]].executor for el in config["deps"]}
                node.set_dependencies(solved_deps)

        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "init" in config:
                node.set_template(config["init"])

        for _,node in enumerate(graph_nodes):
            node.setup_complete()

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

    def __call__(self, input_data):
        res = None

        input_node = [el for el in self.graph_nodes if el["name"] == "_I"][0]
        input_node["inputs"] = input_data
        try:
            while True:
                runnable = [i for i,v in enumerate(self.graph_nodes) if v.is_runnable()]
                if len(runnable) == 0:
                    break
                parallel_jobs = 1
                if len(runnable) > parallel_jobs:
                    runnable = runnable[0:parallel_jobs]
                if parallel_jobs > 1:
                    tds = [threading.Thread(target=self.graph_nodes[i].execute) for i in runnable]
                    for el in tds:
                        el.start()
                    for el in tds:
                        el.join()
                else:
                    for i in runnable:
                        self.graph_nodes[i].execute()
                for i in runnable:
                    res = self.graph_nodes[i]["last_output"]
                    #res = self.graph_nodes[i].execute()
                    config = self.node_configs[i]
                    name = config["name"]
                    rname = "r" + name
                    self.variables[rname] = res
                    self.variables["r"][name] = res
                self._execute_arcs()
        except KeyboardInterrupt:
            print("")
            return [None]
        return res
