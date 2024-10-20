from modules.executors import *
import sys

class GraphNode:

    @staticmethod
    def make_graph_node(graph, node_config):
        node = GraphNode(graph, node_config)
        return node

    def __init__(self,graph,node_config):
        self.graph = graph
        self.free_runs = 0
        self.disable_execution = False

        self.type = node_config["type"]
        self.name = node_config["name"]
        self.path = graph.path + node_config["name"]
        self.config = node_config
        node = {}
        el = node_config
        node_graph_parameters = {"graph":graph,"client":graph.client, "path":self.path,"logger":graph.logger}
        self.executor = ExecutorFactory.makeExecutor(el["type"],node_graph_parameters)
        self.executor.graph = graph
        if isinstance(self.executor,GenericExecutor):
            self.executor.graph_data = node_graph_parameters
            self.executor.properties = {"free_runs": 0, "input_rule":"AND", "input_active": []}
            self.executor.node = self

    def initialize(self):
        if isinstance(self.executor, GenericExecutor):
            self.executor.initialize()

    def _get_input_rule(self):
        if isinstance(self.executor, GenericExecutor):
            props = self.executor.get_properties()
        else:
            self.input_rule = "AND"
            props = None
            if hasattr(self.executor, "get_properties"):
                props = self.executor.get_properties()
            elif hasattr(self.executor, "properties"):
                props = self.executor.properties

        if props is not None:
            self.input_rule = props.get("input_rule","AND")
            if "free_runs" in props:
                self["free_runs"] = props["free_runs"]
            if "input_active" in props:
                self["input_active"] = props["input_active"]
        return self.input_rule

    def setup_complete(self):
        if isinstance(self.executor,GenericExecutor):
            self.executor.setup_complete()

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

        try:
            res = ex(inputs)
        except Exception as e:
            print("Exception: ",e,file=sys.stderr)
            self.graph.logger.log("error", str(e))
            res = []
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
        if isinstance(self.executor,GenericExecutor):
            self.executor.set_dependencies(deps)
        else:
            r = list(deps.values())
            self.executor.set_dependencies(r)

    def set_config(self,args):
        if self.type == "graph":
            self.executor.set_client_parameters(self.graph.client_parameters)
        elif args is None:
            if hasattr(self.executor, "prepare"):
                pass
        elif self.type == "tool":
            self.executor.prepare(args)
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
        if isinstance(self.executor, GenericExecutor):
            self.executor.set_template(init_args)
        else:
            self.executor.load_config(init_args)


    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self,key,value)

