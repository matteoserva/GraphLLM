
from .executors import *
from .executors.common import send_chat,solve_placeholders
from .formatter import PromptBuilder
from .parser import solve_templates
from .common import readfile,merge_params,try_solve_files, PythonInterpreter
from .grammar import load_grammar
from .agent_ops import AgentOps

from .common import get_input
import subprocess
import copy
import json







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




class ToolExecutor(AgentOps):
    pass



class PythonExecutor:
    def __init__(self,*args):
        self.base_subst = "<<<<PYTHONSUBST>>>>"
        self.base_template = self.base_subst
        self.interpreter = PythonInterpreter()
        self.saved_variables = {}
        self.properties = {}
        pass

    def load_config(self,args):
        if len(args)> 0:
            self.base_template = args[0]
        #todo: gestire parametri successivi

    def set_parameters(self,params):
        if "free_runs" in params:
            self.properties["free_runs"] = params["free_runs"]

    def __call__(self,scr, *args):
        self.properties["free_runs"] = 0
        script = self.base_template
        if script.find(self.base_subst) >= 0:
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

        retval = [s,str(globalsParameter)]
        if "_O" in globalsParameter:
            retval = globalsParameter["_O"]
            del globalsParameter["_O"]
            retval.append(s)
            retval.append(str(globalsParameter))
        self.saved_variables = globalsParameter
        return retval

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
        self.free_runs = 0
        self.current_iteration = 0

    def get_properties(self):
        res = {"free_runs":self.free_runs}
        return res

    def load_config(self,args):
        self.base_retval = args
        if not isinstance(args[0],list):
            self.base_retval = [[el] for el in args]
        self.retval = [[] for el in args]

    def __call__(self,args0, *prompt_args):


        if self.current_iteration == 0:
            for i,el in enumerate(self.base_retval):
                self.retval[i] = el
                self.retval[i][0] = solve_placeholders(el[0], args0)

        ret = self.retval[self.current_iteration]

        if not isinstance(ret,list):
            ret = [ret]
        ret[0], _ = solve_templates(ret[0], args0)

        #print(self.retval[self.current_iteration])

        self.current_iteration = (self.current_iteration + 1) % len(self.retval)
        if self.free_runs > 0:
            self.free_runs -= 1
        else:
            self.free_runs = len(self.retval) -1
        return ret

class ExecNode:
    def __init__(self,*args):
        pass

    def load_config(self,args):
        self.args = args

    def __call__(self,*args):
        execArgs = args[0]
        execArgsClean = [str(el) for el in execArgs]
        confArgs = copy.copy(self.args)
        for i in range(len(execArgs)):
            name = "{p:exec" + str(i+1) + "}"
            for j in range(len(self.args)):
                val = confArgs[j]
                v2 = val.replace(name,execArgsClean[i])
                confArgs[j] = v2
        fullargs = confArgs
        concatenatedArgs = "\n----------------\n".join(execArgsClean)
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
        cl_args = args
        if len(cl_args) > 0:
            self.current_prompt,_ = solve_templates(cl_args[0],cl_args[1:])


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
        self.stack = []
        self.cache = None

    def get_properties(self):
        res = self._properties
        return res

    def set_parameters(self,args):
        if "subtype" in args:
            self._subtype = args["subtype"]
            if args["subtype"] == "mux":
                self._properties["input_rule"] = "OR"
            if args["subtype"] == "gate":
                self._properties["input_rule"] = "XOR"
                self._properties["input_active"] = 0

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
        elif self._subtype == "repeat":
            if self.cache is None:
                self.cache = res
                self._properties["free_runs"] = 1
            else:
                res = self.cache
            
        elif self._subtype == "gate":
            numInputs = len(res)
            outval = [None] * numInputs
            input_active = self._properties["input_active"]
            outval[input_active] = res[input_active]
            input_active = (input_active + 1) % numInputs

            self._properties["input_active"] = input_active
            res = outval
        elif self._subtype == "mux":
            if len(res) == 1: #mux nel tempo
                if res[0] == "{p:eos}":
                    res = [self.stack]
                    self.stack = []
                else:
                    self.stack.append(res[0])
                    res = [None]
            else: #mux nello spazio
                l = [el for el in res if el is not None] #TODO: solo uno e mettere da parte gli altri
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
