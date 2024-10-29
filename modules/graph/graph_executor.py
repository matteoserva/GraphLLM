from . import graph_utils
from ..common import readfile,merge_params,try_solve_files


from modules.clients import Client,DummyClient,GLMClient,ONNXClient
from ..grammar import load_grammar

from modules.logging.logger import Logger
import sys
from .graph_node import GraphNode
import queue
from functools import partial

PARALLEL_JOBS=2

class GraphExecutor:
    def __init__(self,executor_config):
        if not isinstance(executor_config, dict):
            executor_config = {"client":executor_config}

        self.stopped_queue = queue.Queue()
        
        client = executor_config["client"]
        if "logger" in executor_config:
            self.logger = executor_config["logger"]
        else:
            self.logger = Logger()

        self.path = executor_config.get("path","") + "/"
        self.client_parameters = executor_config.get("client_parameters",None)

        self.client = client
        self.variables={"c": {}, "r":{}, "_C":{}}
        self.force_stop = False

    def set_client_parameters(self,p):
        self.client_parameters = p

    def load_config(self,cl_args=None):
        try_solve_files(cl_args)

        instructions_raw = None

        clean_config = cl_args[0]
        clean_config = graph_utils.get_clean_config(clean_config)

        self.variables["current_date"] = "23 Jul 2024"
        graph_raw = graph_utils.parse_executor_graph(clean_config)

        # poi consumo gli input con i {}
        for a in graph_raw:
            for i,v in enumerate(a.get("init",[])):
                if v == "{}":
                    a["init"][i] = cl_args[1]
                    cl_args = cl_args[:1] + cl_args[2:]
                pass

        #add output node if there is only one node
        executable_nodes = [el for el in graph_raw if el["type"] != "variable"]
        if len(executable_nodes) == 1:
            obj = {"name": "_O", "type": "copy","exec":[executable_nodes[0]["name"]]}
            graph_raw.append(obj)

        #add command_line node
        input_obj = {"name": "_C", "type": "constant", "init": cl_args}
        graph_raw.insert(0,input_obj)

        #add input node if there is none
        input_obj = {"name": "_I", "type": "copy"}
        graph_raw.insert(0, input_obj)

        node_connections = graph_utils.create_arcs(graph_raw)
        node_configs = graph_raw

        graph_nodes = []
        for el in node_configs:
            node = GraphNode.make_graph_node(self,el)
            graph_nodes.append(node)

        nodes_map = {el["name"]:el for el in graph_nodes}

        node_names = [self.path + el["name"] for el in graph_nodes]
        self.logger.log("names", node_names)

        # step: initialize
        for i, node in enumerate(graph_nodes):
            node.initialize()

        # step: set_parameters
        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            node.set_config(config.get("conf",None))

        # now override command line variables
        # assegno le variabili rimanenti (command line variables)
        for i, v in enumerate(cl_args):
            idx = i
            stri = "c" + str(idx)
            self.variables[stri] = v
            self.variables["c"][str(idx)] = v
            stri = "_C" + str(idx)
            self.variables[stri] = v
            self.variables["_C"][str(idx)] = v
        self.variables["c*"] = cl_args[1:]
        self.variables["_C*"] = cl_args[1:]

        # step: set dependencies
        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "deps" in config:
                solved_deps = {el:nodes_map[config["deps"][el]].executor for el in config["deps"]}
                node.set_dependencies(solved_deps)

        # step: set template
        for i,node in enumerate(graph_nodes):
            config = node_configs[i]
            if "init" in config:
                node.set_template(config["init"])

        # step: setup complete
        for _,node in enumerate(graph_nodes):
            node.setup_complete()

        # preparing the connections
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
            source_outputs = node.get_outputs()
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

    def _notify_stop(self,index):
        self.stopped_queue.put(index)

    def _execute_nodes(self,runnable):
        parallel_jobs = PARALLEL_JOBS
        if len(runnable) > parallel_jobs:
            runnable = runnable[0:parallel_jobs]
        try:
            running_nodes = [self.graph_nodes[i].start(partial(self._notify_stop,i)) for i in runnable ]
        finally:
            stopped_nodes = [self.stopped_queue.get() for i in runnable ]

        for i in runnable:
            res = self.graph_nodes[i]["last_output"]
            
            # res = self.graph_nodes[i].execute()
            config = self.node_configs[i]
            name = config["name"]
            rname = "r" + name
            self.variables[rname] = res
            self.variables["r"][name] = res
            self.last_output = res


    def stop(self):
        self.force_stop = True

    def __call__(self, input_data):
        self.last_output = None
        self.force_stop = False
        input_node = [el for el in self.graph_nodes if el["name"] == "_I"][0]
        input_node["inputs"] = input_data

        if len(input_data) > 0:
            input_nodes = []
            for i,el in enumerate(self.node_configs):
                if el["type"] == "copy" and el.get("conf",{}).get("subtype","") == "input":
                    input_nodes.append(i)
            for i in input_nodes:
                node = self.graph_nodes[i]
                node["outputs"] = input_data
                node.disable_execution = True


        try:
            while not self.force_stop:
                runnable = [i for i, v in enumerate(self.graph_nodes) if v.is_runnable()]
                if len(runnable) == 0:
                    break
                self._execute_nodes(runnable)
                self._execute_arcs()
        except KeyboardInterrupt:
            print("")
            return [None]
        return self.last_output
