from .formatter import PromptBuilder
from .parser import solve_templates
from .common import readfile,merge_params,try_solve_files, PythonInterpreter
from .grammar import load_grammar
from .agent_ops import AgentOps

from .common import get_input
import subprocess
import copy
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

def solve_placeholders(base, confArgs):
        for i in range(len(confArgs)):
            name = "{p:exec" + str(i + 1) + "}"
            val = confArgs[i]
            base = base.replace(name, val)
        return base

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
        res = send_chat(builder,client,self.client_parameters,self.print_response)
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

        self.enabled_input = 0

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

    def _execute_prompt(self):
        prompt = yield
        print("sono thread")
        # send query
        res = self._handle_query(prompt)
        llm_response = yield (1,res)

        while True:
            # call tool
            self.current_iteration += 1
            respo = self._handle_llm_response(llm_response)
            if (respo["command"] == "answer"):
                self.state = "COMPLETE"
                self.answer = respo["args"]
                tool_response = yield (2, respo)
            elif self.current_iteration >= 10:
                yield (0, Exception("llm agent overrun"))
            else:
                tool_response = yield (2, respo)

            if (self.state == "COMPLETE"):

                self._reset_internal_state()
                yield (0, tool_response)
            else:
                res = self._handle_tool_response(tool_response)
                llm_response = yield (1, res)

    def _handle_graph_request(self,inputs):
        outputs = [None] * 3
        true_inputs = len([el for el in inputs if el])
        if(true_inputs != 1):
            throw ("controller: invalid number of inputs")
        if not inputs[self.enabled_input]:
            throw("controller: unexpected input")

        if self.enabled_input == 0:
            self.t1 = self._execute_prompt()
            next(self.t1)

        id, val = self.t1.send(inputs[self.enabled_input])
        self.enabled_input = id
        outputs[id] = val
        inputs[self.enabled_input] = None

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



class PythonExecutor:
    def __init__(self,*args):
        self.base_subst = "<<<<PYTHONSUBST>>>>"
        self.base_template = self.base_subst
        self.interpreter = PythonInterpreter()
        self.saved_variables = {}
        pass

    def load_config(self,args):
        if len(args)> 0:
            self.base_template = args[0]
        #todo: gestire parametri successivi


    def __call__(self,scr, *args):

        script = self.base_template
        for el in scr:
                script = script.replace(self.base_subst,el,1)

        scriptContext = {"_C":scr}
        for el in self.saved_variables:
            if el not in scriptContext:
                scriptContext[el] = self.saved_variables[el]
        #print("scr:", script)
        s = self.interpreter.execute(script,scriptContext)
        globalsParameter = scriptContext
        s=s.rstrip()
        del globalsParameter["_C"]
        self.saved_variables = globalsParameter
        return [s,str(globalsParameter)]

class LlamaTool:
    def __init__(self,*args):
        self.base_subst = "<<<<PYTHONSUBST>>>>"
        self.base_template = self.base_subst
        self.interpreter = PythonInterpreter()
        pass

    def load_config(self,args):
        if len(args)> 0:
            self.base_template = args[0]
        #todo: gestire parametri successivi


    def __call__(self,scr, *args):
        if scr[1]["role"] == "call":
            if scr[0].startswith("<|python_tag|>"):
                script=scr[0][14:]
                s = self.interpreter.execute(script, {})
                s = s.rstrip()
                res = [None,("ipython",s)]
            else:
                res = [None, ("dummy", "dummy")]
        else:
            res = [scr[0],None]
        return res

class ListNode:
    def __init__(self,*args):
        self.free_runs = 1
        self.current_iteration = 0

    def get_properties(self):
        res = {"free_runs":self.free_runs}
        return res

    def load_config(self,args):
        self.free_runs = len(args) - 1
        self.retval = args

    def __call__(self,*prompt_args):
        ret = self.retval[self.current_iteration]
        if not isinstance(ret,list):
            ret = [ret]
        ret[0], _ = solve_templates(ret[0], prompt_args[0])
        ret[0] = solve_placeholders(ret[0], prompt_args[0])
        #print(self.retval[self.current_iteration])
        self.current_iteration += 1
        self.free_runs -= 1
        return ret

class ExecNode:
    def __init__(self,*args):
        pass

    def load_config(self,args):
        self.args = args

    def __call__(self,*args):
        execArgs = args[0]
        confArgs = copy.copy(self.args)
        for i in range(len(execArgs)):
            name = "{p:exec" + str(i+1) + "}"
            for j in range(len(self.args)):
                val = confArgs[j]
                v2 = val.replace(name,execArgs[i])
                confArgs[j] = v2
        fullargs = confArgs
        concatenatedArgs = "\n----------------\n".join(execArgs)
        result = subprocess.run(fullargs,capture_output = True,text = True, input = concatenatedArgs)
        ret = str(result.stdout)
        return ret

class ConstantNode(ListNode):
    def __init__(self,*args):
        super().__init__(*args)

    def load_config(self,args):
        super().load_config([args])


class UserInputNode:
    def __init__(self,*args):
        self.current_prompt = "{}"

    def get_properties(self):
        res = {"input_rule":"OR"}
        return res

    def load_config(self,args):
        cl_args = args[0]
        if len(cl_args) > 0:
            self.current_prompt,_ = solve_templates(cl_args[0],cl_args[1:])
            self.retval = args

    def __call__(self,*args):
        try:
            while self.current_prompt.count("{}") > 0:
                m = [get_input() ]
                self.current_prompt , _ = solve_templates(self.current_prompt,m)
        except EOFError:
            return [None]
        new_prompt = self.current_prompt
        self.current_prompt = "{}"

        return new_prompt

class CopyNode:
    def __init__(self,*args):
        self.parameters = {}
        self._properties = {"input_rule":"AND"}
        self._subtype="copy"

    def get_properties(self):
        res = self._properties
        return res

    def set_parameters(self,args):
        if "subtype" in args:
            self._subtype = args["subtype"]
            if args["subtype"] == "mux":
                self._properties["input_rule"] = "OR"


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
        if self._subtype  == "cast":
            res[0] = str(res[0])
        elif self._subtype == "mux":
            l = [el for el in res if el is not None]
            res = l
        elif self._subtype == "log":
            if "logfile" in self.parameters:
              fn = self.parameters["logfile"]
              with open(fn,"w") as f:
                f.write(res[0])

        elif ("return_attr" in self.parameters):
            attr_name = self.parameters["return_attr"]
            v = res[0]
            base = self._json_parse(v)
            res[0] = base[attr_name]
        return res
