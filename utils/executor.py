from .formatter import PromptBuilder
from .parser import solve_templates
from .common import readfile,merge_params
from .grammar import load_grammar
from . import graph

def parse_files(cl_args):
    for i, el in enumerate(cl_args):
        try:
            cl_args[i] = readfile(el)
        except:
            pass
    return cl_args

def send_chat(builder,client,client_parameters=None,print_response=True):
    r = client.send_prompt(builder,params=client_parameters)
    ret = ""
    for line in r:
        if print_response:
             print(line, end="", flush=True)
        ret = ret + line
    if print_response and print_response != "partial":
        print("")
    return ret


class BaseExecutor:
    def __init__(self,client):
        builder = PromptBuilder()
        builder.load_model(client.get_model_name())
        self.builder=builder
        self.client = client
        self.print_prompt=True
        self.print_response=True
        self.current_prompt="{}"
        self.client_parameters = None

    def set_client_parameters(self,p):
        self.client_parameters = p

    def load_config(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass
        new_prompt, _ = solve_templates(self.current_prompt,cl_args)
        self.current_prompt = new_prompt

    def get_prompt_len(self):
        return self.current_prompt.count("{}")

    def basic_exec(self,text_prompt):
        m = text_prompt
        client = self.client
        builder = self.builder
        messages = builder.add_request(m)
        prompt = builder._build()
        if self.print_prompt:
            print(builder._build(),end="")
        res = send_chat(builder,client,self.client_parameters,self.print_response)
        messages = builder.add_response(str(res))
        return res

class StatelessExecutor(BaseExecutor):
    def __init__(self,client):
        super().__init__(client)

    def __call__(self,prompt_args):
        m ,_ = solve_templates(self.current_prompt,prompt_args)
        self.builder.reset()

        res = self.basic_exec(m)
        return res

class StatefulExecutor(BaseExecutor):
    def __init__(self,client):
        super().__init__(client)

    def __call__(self,prompt_args):
        m ,_ = solve_templates(self.current_prompt,prompt_args)
        self.current_prompt="{}"

        res = self.basic_exec(m)
        return res

class SequenceExecutor:
    def __init__(self,client):

#       self.client = client
        self.execRow = StatelessExecutor(client)
        self.client_parameters = None

    def set_client_parameters(self,p):
        self.execRow.set_client_parameters(p)

    def load_config(self,cl_args=None):
        parse_files(cl_args)
        for el in cl_args[1:]:
            cl_args[0].replace("{}",el,1)
        self.instructions_raw = cl_args[0]
        return cl_args

    def _execute_row(self,inputs,variables={}):
        for i in range(len(inputs)):
            try:
                p=readfile(inputs[i])
                inputs[i] = p
            except:
                pass
        m,_ = solve_templates(inputs[0],inputs[1:],variables)
        res = self.execRow([m])
        return res

    def _execute_list(self,instructions, cl_args):
        pos = 1
        variables={}
        res = None
        var_c = ["base"]*(1+len(cl_args))
        var_r = ["base"]*(1+len(instructions))
        for i,v in enumerate(cl_args):
            idx = i+1
            var_c[idx] = v
            stri = "c" + str(idx)
            variables[stri] = v
        variables["c"] = var_c
        variables["r"] = var_r
        for instr in instructions:
            res = self._execute_row(instr,variables)
            fn = "/tmp/llm_exec_" + str(pos) + ".txt"
            f = open(fn,"w")
            f.write(res)
            f.close()
            variables[str(pos)] = res
            var_r[pos] = res
            var_r[0] = res #pos 0 contiene sempre l'ultima
            pos = pos + 1
        return res

    def __call__(self,prompt):
        # for i,el in enumerate(prompt):
        #     try:
        #         prompt[i] = readfile(el)
        #     except:
        #         pass
        lista_istruzioni = self.instructions_raw
        instructions = [ [ es  for es in el.strip().split(" ") if len(es) > 0] for el in lista_istruzioni.strip().split("\n") if not el.startswith("#")]
        res = self._execute_list(instructions, prompt)
        return res





class GraphExecutor:
    def __init__(self,client):

        #self.execRow = StatelessExecutor(client)
        self.client = client
        self.client_parameters = None
        self.variables={"c": {}, "r":{}}

    def set_client_parameters(self,p):
        self.client_parameters = p
        #self.execRow.set_client_parameters(p)

    def _make_node(self,node_config):
        node = {}
        el = node_config
        if el["type"] == "stateless":
            ex_args = el["exec"]
            node["executor"] = StatelessExecutor(self.client)
            if "init" in el:
                init_args = el["init"]
                for i, v in enumerate(init_args):
                    init_args[i], _ = solve_templates(init_args[i], [], self.variables)
                node["executor"].load_config(el["init"])
            executor_parameters = self.client_parameters
            if "conf" in el and "grammar" in el["conf"]:
                grammarfile = el["conf"]["grammar"]
                grammar = load_grammar(grammarfile)
                new_obj = {grammar["format"]: grammar["schema"]}
                executor_parameters = merge_params(executor_parameters, new_obj)
                pass

            node["executor"].set_client_parameters(executor_parameters)
        elif el["type"] == "command_line":
            val = el["init"]

            def dummy_return(d):
                return val

            node["executor"] = dummy_return
        return node

    def load_config(self,cl_args=None):
        parse_files(cl_args)
        for i,v in enumerate(cl_args):
            idx = i
            stri = "c" + str(idx)
            self.variables[stri] = v
            self.variables["c"][str(idx)] = v
        instructions_raw = None
        graph_raw = graph.parse_executor_graph(cl_args[0],cl_args[1:])
        node_connections = graph.create_arcs(graph_raw)
        node_configs = graph_raw


        graph_nodes = []
        for el in node_configs:
            node = self._make_node(el)
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