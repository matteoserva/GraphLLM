from ..formatter import PromptBuilder
from ..parser import solve_templates
from .common import send_chat,solve_placeholders
from ..common import readfile
from functools import partial

class BaseExecutor:
    def __init__(self,node_graph_parameters):
        self.print_prompt=True
        self.print_response=True
        self.current_prompt="{}"
        self.client_parameters = None
        if "client" in node_graph_parameters:
           self.set_dependencies({"client":node_graph_parameters["client"]})
        self.logger = node_graph_parameters["logger"]
        self.path = node_graph_parameters["path"]

    def set_dependencies(self,d):
        if "client" in d:
           client = d["client"]
           builder = PromptBuilder()
           builder.load_model(client.get_model_name())
           self.client = client
           self.builder=builder

    def set_client_parameters(self,p):
        self.client_parameters = p

    def set_param(self,key,value):
        if key in ["force_system","sysprompt"]:
            self.builder.set_param(key, value)
        elif key == "print_prompt":
            self.print_prompt = value

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
        if text_prompt == "{p:eos}":
            self.builder.reset()
            return ["{p:eos}"]
        m = text_prompt
        client = self.client
        builder = self.builder
        if isinstance(m,tuple):
            messages = builder.add_request(m[1],m[0])
        else:
            messages = builder.add_request(m)

        if bool(self.print_prompt):
            x = self.print_prompt
            if isinstance(x, (int, float, complex)) and not isinstance(x, bool):
                self.print_prompt -= 1
            prompt = builder._build()
            print(prompt,end="")
        res = send_chat(builder,client,self.client_parameters,self.print_response,logger_print=partial(self.logger.log,"print",self.path))
        resp = [res,{"role":"assistant"}]

        if "stopped_word" in client.prompt_metadata and client.prompt_metadata["stopped_word"] and client.prompt_metadata["stopping_word"] == "<|eom_id|>":
            messages = builder.add_response(str(res),"call")
            resp = [res, {"role":"call"}]
        else:
            messages = builder.add_response(str(res))
        return resp



class StatelessExecutor(BaseExecutor):
    def __init__(self,client):
        super().__init__(client)

    def __call__(self,prompt_args):
        m ,_ = solve_templates(self.current_prompt,prompt_args)
        m = solve_placeholders(m,prompt_args)
        self.builder.reset()

        res = self.basic_exec(m)
        return res

class StatefulExecutor(BaseExecutor):
    def __init__(self,client):
        super().__init__(client)

    def __call__(self,prompt_args):
        if len(prompt_args) > 0 and isinstance(prompt_args[0],tuple):
            m = prompt_args[0]
        else:
            m ,_ = solve_templates(self.current_prompt,prompt_args)
            m = solve_placeholders(m, prompt_args)
        self.current_prompt="{}"

        res = self.basic_exec(m)
        return res