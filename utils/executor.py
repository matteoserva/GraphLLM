from .formatter import PromptBuilder
from .parser import solve_templates
from .common import readfile

def send_chat(builder,client):
    r = client.send_prompt(builder)
    ret = ""
    for line in r:
        print(line, end="", flush=True)
        ret = ret + line
    print("")
    return ret

class StatelessExecutor:
    def __init__(self,client):
        builder = PromptBuilder()
        builder.load_model(client.get_model_name())
        self.builder=builder
        self.client = client


    def __call__(self,m):
        builder = self.builder
        client = self.client

        builder.reset()
        messages = builder.add_request(m)
        prompt = builder._build()
        print(builder._build(),end="")
        res = send_chat(builder,client)
        messages = builder.add_response(str(res))
        return res

class StatefulExecutor:
    def __init__(self,client):
        builder = PromptBuilder()
        builder.load_model(client.get_model_name())
        self.builder=builder
        self.client = client
        self.print_prompt = True

    def __call__(self,m):
        builder = self.builder
        client = self.client

        messages = builder.add_request(m)
        prompt = builder._build()
        if self.print_prompt:
            print(builder._build(),end="")
        res = send_chat(builder,client)
        messages = builder.add_response(str(res))
        return res
    
class SequenceExecutor:
    def __init__(self,client):

        self.client = client
        self.execRow = StatelessExecutor(client)

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
        res = self.execRow(m)
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
