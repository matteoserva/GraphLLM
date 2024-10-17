from . import graph_utils
from ..common import readfile,merge_params,try_solve_files


from modules.clients import Client,DummyClient,GLMClient,ONNXClient
from ..grammar import load_grammar
import threading
from modules.logging.logger import Logger
import sys
from .graph_node import GraphNode, _make_graph_node


PARALLEL_JOBS=2

class GraphExecutor:
    def __init__(self,executor_config):
        if not isinstance(executor_config, dict):
            executor_config = {"client":executor_config}

        client = executor_config["client"]
        if "logger" in executor_config:
            self.logger = executor_config["logger"]
        else:
            self.logger = Logger()
        if "path" in executor_config:
            self.path = executor_config["path"] + "/"
        else:
            self.path = "/"

        if "client_parameters" in executor_config:
            self.client_parameters = executor_config["client_parameters"]
        else:
            self.client_parameters = None

        self.client = client
        self.variables={"c": {}, "r":{}}
        self.force_stop = False

    def set_client_parameters(self,p):
        self.client_parameters = p
        #self.execRow.set_client_parameters(p)



    def load_config(self,cl_args=None):
        try_solve_files(cl_args)

        instructions_raw = None

        clean_config = cl_args[0]
        clean_config = graph_utils.get_clean_config(clean_config)


        self.variables["current_date"] = "23 Jul 2024"
        #clean_config = clean_config.replace("{v:current_date}",self.variables["current_date"])
        graph_raw = graph_utils.parse_executor_graph(clean_config)

        # assegno le variabili
        # for el in graph_raw:
        #     if el["type"] == "variable":
        #         conf = el.get("conf",{})
        #         name = conf.get("name")
        #         value = conf.get("value")
        #         self.variables[name] = value

        # poi consumo gli input con i {}
        for a in graph_raw:
            for i,v in enumerate(a.get("init",[])):
                if v == "{}":
                    a["init"][i] = cl_args[1]
                    cl_args = cl_args[:1] + cl_args[2:]
                pass

        # assegno le variabili rimanenti (command line variables)
        for i, v in enumerate(cl_args):
            idx = i
            stri = "c" + str(idx)
            self.variables[stri] = v
            self.variables["c"][str(idx)] = v
        self.variables["c*"] = cl_args[1:]

        # # connetto i virtual node
        # virtual_sinks = {el["conf"]["name"]: el["name"] for el in graph_raw if el["type"] == "virtual_sink"}
        # virtual_sources = [el for el in graph_raw if el["type"] == "virtual_source"]
        # for el in virtual_sources:
        #     ident = el["conf"]["name"]
        #     source = virtual_sinks[ident]
        #     el["exec"] = [source]


        #add output node if there is only one node
        executable_nodes = [el for el in graph_raw if el["type"] != "variable"]
        if len(executable_nodes) == 1:
            obj = {"name": "_O", "type": "copy","exec":[executable_nodes[0]["name"]]}
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

        node_names = [self.path + el["name"] for el in graph_nodes]
        self.logger.log("names", node_names)

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

    def node_runner(self,func,sem):
        try:
            func()
        finally:
            sem.wait()

    def stop(self):
        self.force_stop = True

    def __call__(self, input_data):
        res = None
        self.force_stop = False
        input_node = [el for el in self.graph_nodes if el["name"] == "_I"][0]
        input_node["inputs"] = input_data
        try:
            while not self.force_stop:
                runnable = [i for i,v in enumerate(self.graph_nodes) if v.is_runnable()]
                if len(runnable) == 0:
                    break
                parallel_jobs = PARALLEL_JOBS
                if len(runnable) > parallel_jobs:
                    runnable = runnable[0:parallel_jobs]
                if True or parallel_jobs > 1:
                    self.logger.log("running", [self.graph_nodes[j].path for j in runnable])
                    sem = threading.Barrier(1+len(runnable))
                    tds = [threading.Thread(target=self.node_runner,args=[self.graph_nodes[i].execute,sem],daemon=True) for i in runnable]
                    for el in tds:
                        el.start()
                    sem.wait() #this can except
                else:
                    for i in runnable:
                        self.logger.log("running", [i])
                        self.graph_nodes[i].execute()
                for i in runnable:
                    res = self.graph_nodes[i]["last_output"]
                    self.logger.log("output", self.path + self.graph_nodes[i]["name"],res)
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
