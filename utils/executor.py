from .formatter import PromptBuilder
from .parser import solve_templates
from .common import readfile,merge_params,try_solve_files
from .grammar import load_grammar
from .agent_ops import AgentOps
import json

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
        self.print_prompt=True
        self.print_response=True
        self.current_prompt="{}"
        self.client_parameters = None
        if client is not None:
           self.set_dependencies({"client":client})

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
        if key == "force_system":
            self.builder.set_param(key, value)

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

        self.execRow = StatelessExecutor(client)
        self.client_parameters = None

    def set_client_parameters(self,p):
        self.execRow.set_client_parameters(p)

    def load_config(self,cl_args=None):
        cl_args[0] = try_solve_files([cl_args[0]])[0]
        for el in cl_args[1:]:
            cl_args[0] = cl_args[0].replace("{}",el,1)
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

class AgentController:
    def __init__(self, *args):
        self.current_prompt = ""
        self.base_prompt = ""
        self.tokens=["Thought: ","Action:","Inputs:","Observation: "]
        self.state = "INIT"
        self.current_iteration = 0
        self.answer = ""

    def set_parameters(self,arg):
        if "tokens" in arg:
            self.tokens = arg["tokens"]

    def get_properties(self):
        res = {"input_rule":"OR"}
        return res

    def _reset_internal_state(self):
        self.state = "INIT"
        self.current_prompt = self.base_prompt
        self.current_iteration = 0

    def load_config(self,args):

        template_args =  try_solve_files(args)
        self.base_prompt , _ = solve_templates("{}", template_args)

        self._reset_internal_state()
        pass

    def set_dependencies(self,args):
        self.ops_executor = args[0]

    def _handle_tool_response(self,prompt_args):


        new_observation = str(prompt_args)
        if len(new_observation) > 0:
            new_observation = self.tokens[3] + new_observation + "\n" + self.tokens[0]
        self.current_prompt += new_observation
        return self.current_prompt

    def _handle_query(self,prompt_args):
        ops_string = self.ops_executor.get_formatted_ops()
        self.current_prompt ,_ = solve_templates(self.base_prompt, [ops_string])
        return self.current_prompt

    def _handle_llm_response(self,resp):

        resp = self._clean_response(resp)
        self.current_prompt += resp
        respo = self._parse_response(resp)
        respo["raw"] = resp

        return respo

    def _handle_graph_request(self,inputs):
        outputs = [None] * 3

        if inputs[0] is not None:
            outputs[1] = self._handle_query(inputs[0])
            inputs[0] = None
        elif inputs[1] is not None:
            self.current_iteration += 1
            respo = self._handle_llm_response(inputs[1])
            if (respo["command"] == "answer"):
                self.state = "COMPLETE"
                self.answer = respo["args"]
                outputs[2] = respo
            elif self.current_iteration >= 10:
                outputs[0] = Exception("llm agent overrun")
            else:
                outputs[2] = respo
            inputs[1] = None
        elif inputs[2] is not None:
            if (self.state == "COMPLETE"):
                outputs[0] = inputs[2]
                self._reset_internal_state()

            else:
                outputs[1] = self._handle_tool_response(inputs[2])
            inputs[2] = None

        return outputs

    def __call__(self,*args,**kwargs):
        return self._handle_graph_request(*args,**kwargs)

    def _clean_response(self, resp):
        resp = resp.strip()
        while "\n\n" in resp:
           resp = resp.replace("\n\n","\n")
        resp = resp.split("\nObservation")[0]
        resp = resp+"\n"
        return resp

    def _parse_response(self,resp):
        comando = resp[resp.find(self.tokens[1]) + len(self.tokens[1]):].split("\n")[0].strip()
        if comando.find("(") >= 0:  # forma compatta comando(parametri)
            c1 = comando.split("(")
            comando = c1[0].strip()
            parametri = c1[1][:-1]
        else:
            parametri = resp[resp.find("Inputs:") + 7:].strip()

        if resp.find("Answer:") >= 0:
            comando = "answer"
            parametri = resp[resp.find("Answer:") + 7:].strip().split("\n")[0]
        resp = {"command":comando,"args":parametri}

        return resp


class ToolExecutor(AgentOps):
    pass

from io import StringIO
from contextlib import redirect_stdout
import builtins

class PythonExecutor:
    def __init__(self,*args):
        
        self.whitelist = ["sum","range","int"]

        self.base_subst = "<<<<PYTHONSUBST>>>>"
        self.base_template = self.base_subst
        pass

    def load_config(self,args):
        if len(args)> 0:
            self.base_template = args[0]
        #todo: gestire parametri successivi


    def __call__(self,scr, *args):

        script = self.base_template
        for el in scr:
            #if self.base_subst in script:
                script = script.replace(self.base_subst,el,1)
            #else:
            #    script = script + str(el)
            
        safe_builtins = {'print': print, 'dir': dir}
        for el in self.whitelist:
             safe_builtins[el] = getattr(builtins,el)

        globalsParameter = {'__builtins__' : safe_builtins}
        globalsParameter['__builtins__']["_C"] = scr
        f = StringIO()
        print("scr:", script)
        #flocals = {"_C" : scr}
        with redirect_stdout(f):
              exec(script, globalsParameter, globalsParameter)
        s = f.getvalue()
        s=s.rstrip()
        del globalsParameter['__builtins__']
        #print("ret:", s)
        return [s,str(globalsParameter)]

class ConstantNode:
    def __init__(self,*args):
        pass

    def load_config(self,args):
        self.retval = args

    def __call__(self,*args):
        ret = [el for el in self.retval]
        return ret



class CopyNode:
    def __init__(self,*args):
        self.parameters = {}

    def set_parameters(self,args):
        self.parameters = args

    def _json_parse(self,text):
        r2 = text.find("{")
        decoder = json.JSONDecoder()
        val = decoder.raw_decode(text, r2)
        if isinstance(val,tuple):
            val = list(val)
            val = val[0]
        return val

    def __call__(self,*args):

        res = list(*args)
        if "subtype" in self.parameters:
            if self.parameters["subtype"] == "cast":
                res[0] = str(res[0])

            elif ("return_attr" in self.parameters):
                attr_name = self.parameters["return_attr"]
                v = res[0]
                base = self._json_parse(v)
                res[0] = base[attr_name]
        return res
