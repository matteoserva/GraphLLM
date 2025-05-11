from modules.formatter import PromptBuilder
from modules.formatter import solve_templates
from modules.executors.common import solve_placeholders,solve_prompt_args
from modules.common import readfile, merge_params
from functools import partial
from modules.executors.common import GenericExecutor,ExecutorOutput
from modules.grammar import load_grammar,load_grammar_text
from modules.clients.client import Client


class ClientCallback:
    def __init__(self, print_response,logger_print):
        self.print_response = print_response
        self.logger_print = logger_print

    def __call__(self, line):
        if self.print_response:
            self.logger_print(line, end="", flush=True)

def send_chat(builder,client,client_parameters=None,print_response=True, logger_print=print):
    callback = ClientCallback(print_response,logger_print)
    ret = client.send_prompt(builder,params=client_parameters,callback = callback)
    if print_response and print_response != "partial":
        logger_print("")
    return ret

class LlmExecutor(GenericExecutor):
    def __init__(self,node_graph_parameters):
        super().__init__(node_graph_parameters)
        self.print_prompt=True
        self.print_response=True
        self.current_prompt="{}"
        self.client_parameters = None
        self.sysprompt = None
        self.builder = PromptBuilder()
        if "client" in node_graph_parameters:
           self.set_dependencies({"client":node_graph_parameters["client"]})
        self.logger = node_graph_parameters["logger"]
        self.path = node_graph_parameters.get("path","/")
        self.pending_config={}

    def set_parameters(self,args):
            executor_parameters = {}
            if hasattr(self,"graph"):
                executor_parameters = self.graph.client_parameters
            self._set_client_parameters(executor_parameters)
            new_obj = {}
            for key in ["stop", "n_predict","temperature","top_k"]:
                if key in args:
                    new_obj[key] = args[key]

            if "grammar" in args:
                self.pending_config["grammar"] = args["grammar"] 

            executor_parameters = merge_params(executor_parameters, new_obj)
            self._set_client_parameters(executor_parameters)

            for key in ["force_system","print_prompt","sysprompt","print_response"]:
                if key in args:
                    self._set_param(key,args[key])
                    
            for key in ["client"]:
                if key in args:
                    p = {key: args[key]}
                    self.set_dependencies(p)


    def set_dependencies(self,d):
        if "client" in d:
           client = d["client"]
           if isinstance(client,str): # da conservare in caso il client arrivi dal graph
               client = Client.get_client(client)
           builder = self.builder
           try:
               formatter_config = client.get_formatter_config()
           except:
               formatter_config = client.get_model_name()
           #builder.load_model(formatter_config)
           self.client = client


    def _set_client_parameters(self,p):
        self.client_parameters = p

    def _set_param(self,key,value):
        if key in ["sysprompt"]:
            self.sysprompt = value
        elif key in ["force_system","sysprompt"]:
            self.builder.set_param(key, value)
        elif key == "print_prompt":
            self.print_prompt = value
        elif key == "print_response":
            self.print_response = value

    def set_template(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass
        new_prompt, _ = solve_templates(self.current_prompt,cl_args)
        if new_prompt != "":
            self.current_prompt = new_prompt

    def get_prompt_len(self):
        return self.current_prompt.count("{}")

    def send_chat(self,builder,logger_print):
        res = send_chat(builder, self.client, self.client_parameters, self.print_response, logger_print=logger_print)
        response = {"role": "assistant", "content": res}
        client = self.client
        if hasattr(client,"prompt_metadata") and "stopped_word" in client.prompt_metadata and client.prompt_metadata["stopped_word"] and client.prompt_metadata["stopping_word"] == "<|eom_id|>":
            response = {"role": "call", "content": res}
        return response

    def basic_exec(self,text_prompt):

        m = text_prompt
        client = self.client
        builder = self.builder

        if bool(self.print_prompt):
            x = self.print_prompt
            if isinstance(x, (int, float, complex)) and not isinstance(x, bool):
                self.print_prompt -= 1

        res = self.send_chat(self.builder,logger_print=self.node.print)
        builder.add_response(res["content"], res["role"])
        self.builder.set_serialize_format("last")
        out0 = self.builder.to_string("last")
        resp = [out0,res]

        return resp

    def setup_complete(self):
        if "grammar" in self.pending_config:
            new_obj = {}
            executor_parameters = self.client_parameters
            grammar = self.pending_config["grammar"]
            if isinstance(grammar,dict):
                    
                    print(grammar)
                    varname = list(grammar.keys())[0].split(":",1)[-1] # {'v:nome': None} -> nome
                    value = self.graph.variables[varname]
                    grammar = load_grammar_text(value)
                    new_obj[grammar["format"]] = grammar["schema"]
            elif grammar in self.graph.variables:
                    varname = grammar
                    value = self.graph.variables[varname]
                    grammar = load_grammar_text(value)
                    new_obj[grammar["format"]] = grammar["schema"]
            else:
                    grammarfile = grammar
                    grammar = load_grammar(grammarfile)
                    new_obj[grammar["format"]] = grammar["schema"]
                    
            executor_parameters = merge_params(executor_parameters, new_obj)
            self._set_client_parameters(executor_parameters)        
        
        self.pending_config = {}
    
        if self.sysprompt is not None:
            variables = self.graph_data["graph"].variables
            new_value, _ = solve_templates(self.sysprompt, [], variables)
            self.builder.set_param("sysprompt", new_value)


    def __call__(self, prompt_args):
        builder = self.builder

        if len(prompt_args) > 0 and isinstance(prompt_args[0], str) and prompt_args[0] ==  "{p:eos}":
            self.builder.reset()
            return ["{p:eos}"]
        elif len(prompt_args) > 0 and isinstance(prompt_args[0], dict) and "role" in prompt_args[0]:
            m = prompt_args[0]
            self.current_prompt = "{}"
            builder.add_request(prompt_args[0]["content"], prompt_args[0]["role"])

        elif len(prompt_args) > 0 and isinstance(prompt_args[0], tuple):
            m = prompt_args[0]
            self.current_prompt = "{}"
            builder.add_request(m[1], m[0])
        elif self.node_type == "stateful":
            m ,_ = solve_templates(self.current_prompt,prompt_args)
            m = solve_placeholders(m, prompt_args)
            self.current_prompt="{}"
            builder.add_request(m,"user",self.node.graph.variables)
        else:
            m = solve_prompt_args(self.current_prompt, prompt_args)
            self.builder.reset()
            builder.add_request(m,"user",self.node.graph.variables)


        res = self.basic_exec(m)
        res = [ExecutorOutput(el,{"source_llm":self.node.name}) for el in res]
        return res


class StatelessExecutor(LlmExecutor):
    node_type = "stateless"

class StatefulExecutor(LlmExecutor):
    node_type = "stateful"

