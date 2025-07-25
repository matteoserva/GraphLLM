from . import graph_utils
from ..common import try_solve_files

from modules.client_api.logger import Logger
from .graph_node import GraphNode
import queue
from functools import partial
from .common import GraphException
from modules.executors.common import ExecutorOutput
from modules.executors.common import GenericExecutor

PARALLEL_JOBS=2



class GraphExecutor(GenericExecutor):
    properties = {"free_runs": 0, "input_rule":"AND", "wrap_input": False, "input_active": []}
    def __init__(self,executor_config):
        if not isinstance(executor_config, dict):
            executor_config = {"client":executor_config}
        self.executor_config = executor_config
        self.stopped_queue = queue.Queue()
        
        client = executor_config["client"]
        self.logger = executor_config.get("logger",Logger())

        self.path = executor_config.get("path","") + "/"
        self.client_parameters = executor_config.get("client_parameters",None)

        self.client = client
        self.variables={"c": {}, "r":{}, "_C":{}}
        self.force_stop = False

    def set_client_parameters(self,p):
        self.client_parameters = p

    def set_template(self,*args,**kwargs):
        return self.load_config(*args,**kwargs)

    def load_config(self,cl_args=None):
        try_solve_files(cl_args)

        instructions_raw = None

        clean_config = cl_args[0]
        clean_config = graph_utils.get_clean_config(clean_config)

        self.variables["current_date"] = "23 Jul 2024"
        graph_raw = graph_utils.parse_executor_graph(clean_config)

        # poi consumo gli input con i {}
        cl_args_old = cl_args
        for a in graph_raw:
            for i,v in enumerate(a.get("init",[])):
                if v == "{}":
                    a["init"][i] = cl_args[1]
                    cl_args = cl_args[:1] + cl_args[2:]
                pass
        cl_args = cl_args_old

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

        # preparing the connections
        for i,el in enumerate(node_connections):
            num_inputs = len(el["deps"])
            num_outputs = len(el["forwards"])
            graph_nodes[i]["inputs"] = [None] * num_inputs
            graph_nodes[i]["outputs"] = [None] * num_outputs
            graph_nodes[i]["forwards"] = el["forwards"]
            graph_nodes[i]["backwards"] = el["deps"]

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

        self.graph_nodes = graph_nodes
        self.node_configs = node_configs
        #self.node_connections = node_connections
        return cl_args


    def _is_runnable(self,node_index):
        node = self.graph_nodes[node_index]

        missing_inputs = len([el for el in node["inputs"] if el is None])
        blocked_outputs = len([el for el in node["outputs"] if not el is None])

        runnable = (missing_inputs + blocked_outputs) == 0
        return runnable

    def _execute_arcs(self,running):
        for node_index,node in enumerate(self.graph_nodes):
            if node_index in running:
                continue
            source_outputs = node.get_outputs()
            forwards_list = node["forwards"]

            for source_port,current_output in enumerate(source_outputs):
                if source_port >= len(forwards_list):
                    node["outputs"][source_port] = None
                    continue

                forwards = forwards_list[source_port]
                if isinstance(current_output,ExecutorOutput) and "destination" in current_output.meta:
                    dest_tuple = current_output.meta["destination"]
                    dest_node = [i for i,el in enumerate(self.graph_nodes) if el.name == dest_tuple[0]][0]
                    dest_tuple = (dest_node,dest_tuple[1])
                    forwards = [dest_tuple]
                    pass
            #for source_port,forwards in enumerate(forwards_list):
                current_output = source_outputs[source_port]
                destinations_busy = len([i for i,p in forwards if i in running]) > 0
                
                destination_inputs = [self.graph_nodes[i]["inputs"][p] for i,p in forwards]
                destination_ready = len([el for el in destination_inputs if el is not None]) == 0
                source_ready = current_output is not None
                if destinations_busy or (not source_ready) or (not destination_ready):
                    continue

                if isinstance(current_output, ExecutorOutput) and "destination" in current_output.meta:
                    del current_output.meta["destination"]

                for di,dp in forwards:
                    self.graph_nodes[di]["inputs"][dp] = current_output
                node["outputs"][source_port] = None
                pass

    def _notify_stop(self,index, extra=None):
        self.stopped_queue.put(extra if extra else index)

    def _launch_nodes(self,runnable):
        _ = [self.graph_nodes[i].start(partial(self._notify_stop,i)) for i in runnable ]
        return runnable
        
    def _notify_graph_started(self):
        for el in self.graph_nodes:
            el._graph_started()
    
    def _notify_graph_stopped(self):
        for el in self.graph_nodes:
            el._graph_stopped()

    def _get_completions(self, timeout):
        try:
            completed = [self.stopped_queue.get(timeout)]
        except queue.Empty:
            completed = []

        while not self.stopped_queue.empty():
            completed += [self.stopped_queue.get()]

        for i in completed:
            if isinstance(i,Exception):
                raise GraphException(i)
        for i in completed:
            res = self.graph_nodes[i]["outputs"]
            
            # res = self.graph_nodes[i].execute()
            config = self.node_configs[i]
            name = config["name"]
            rname = "r" + name
            self.variables[rname] = res
            self.variables["r"][name] = res

            
        return completed
        


    def stop(self):
        self.force_stop = True

    # this is generated by the parent graph
    # not called when this graph stops naturally
    def graph_stopped(self):
        self.stop()

    def __call__(self, input_data):
        self.outputs = None
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
                while len(node["inputs"]) < len(input_data):
                    node["inputs"].append(None)
                for i, el in enumerate(input_data):
                    node["inputs"][i] = el

        output_nodes = []
        for i, el in enumerate(self.node_configs):
            if el["type"] == "copy" and el.get("conf", {}).get("subtype", "") == "output":
                output_nodes.append(i)

        running = []
        max_parallel_jobs = PARALLEL_JOBS
        self._notify_graph_started()
        try:
            while not self.force_stop:
                runnable = [i for i, v in enumerate(self.graph_nodes) if v.is_runnable() and i not in running]

                if len(runnable) == 0 and len(running) == 0:
                    break
                if len(running) < max_parallel_jobs:
                    max_num_launched = max_parallel_jobs - len(running)
                    runnable = runnable[:max_num_launched]
                    running += self._launch_nodes(runnable)
                if len(running) > 0:
                    completed = self._get_completions(timeout=1.0)
                    if len(completed) == 0:
                        self.logger.log("keepalive")
                    if len(completed) > 0 and len(output_nodes) == 0:
                        self.outputs = self.graph_nodes[completed[-1]]["outputs"][:]
                    elif len(output_nodes) > 0 and output_nodes[0] in completed:
                        self.outputs = self.graph_nodes[output_nodes[0]]["outputs"][:]

                    running = [i for i in running if i not in completed]
                self.logger.log("running", running)
                self._execute_arcs(running)
            if self.force_stop:
                raise GraphException("graph force stopped")
        except KeyboardInterrupt as e:
            print("")
            raise e from None
        finally:
            self._notify_graph_stopped()
        return self.outputs
