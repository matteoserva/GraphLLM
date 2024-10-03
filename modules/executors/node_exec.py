import copy
import subprocess
from ..common import PythonInterpreter
from ..common import readfile

class PythonExecutor:
    def __init__(self,*args):
        self.base_subst = "<<<<PYTHONSUBST>>>>"
        self.base_template = self.base_subst
        self.interpreter = PythonInterpreter()
        self.saved_variables = {}
        self.properties = {}
        self.logger = args[0]["logger"]
        self.path = args[0].get("path", "/")
        pass

    def load_config(self,args):
        for i,el in enumerate(args):
            try:
                args[i] = readfile(el)
            except:
                pass
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

        if len(s) > 0:
            self.logger.log("print",self.path,s+"\n")
        if "_O" in globalsParameter:

            retval = globalsParameter["_O"]
            del globalsParameter["_O"]
            retval.append(s)
            retval.append(str(globalsParameter))
        self.saved_variables = globalsParameter
        return retval





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