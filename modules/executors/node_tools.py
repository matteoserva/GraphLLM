from ..agent_tools import AgentOps
from ..common import PythonInterpreter

class ToolExecutor(AgentOps):
    pass

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