from .formatter import PromptBuilder
from .parser import solve_templates
from .common import readfile

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

        self.client = client
        self.execRow = StatelessExecutor(client)
        self.client_parameters = None

    def set_client_parameters(self,p):
        self.execRow.set_client_parameters(p)

    def load_config(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass
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
        for i,v in enumerate(cl_args):
            idx = i+1
            stri = "c" + str(idx)
            variables[stri] = v
        for instr in instructions:
            res = self._execute_row(instr,variables)
            fn = "/tmp/llm_exec_" + str(pos) + ".txt"
            f = open(fn,"w")
            f.write(res)
            f.close()
            variables[str(pos)] = res
            pos = pos + 1
        return res

    def __call__(self,prompt):
        # for i,el in enumerate(prompt):
        #     try:
        #         prompt[i] = readfile(el)
        #     except:
        #         pass
        lista_istruzioni = self.instructions_raw
        instructions = [ [ es  for es in el.strip().split(" ") if len(es) > 0] for el in lista_istruzioni.strip().split("\n")]
        res = self._execute_list(instructions, prompt)
        return res
