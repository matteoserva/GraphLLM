from modules.common import PythonInterpreter
from modules.common import readfile
from modules.executors.common import GenericExecutor
from modules.tool_call.tools_factory import ToolsFactory

class PythonExecutor(GenericExecutor):
    node_type = "python"
    def __init__(self,*args):
        self.base_subst = "<<<<PYTHONSUBST>>>>"
        self.base_template = self.base_subst
        self.interpreter = PythonInterpreter()
        self.saved_variables = {}
        self.properties = {}
        self.logger = args[0]["logger"]
        self.path = args[0].get("path", "/")

        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tool_classes(only_default=False)
        tool_runner = tools_factory.make_tool_runner(tools_list, args[0])
        self.tools = tool_runner
        pass

    def set_template(self,args):
        for i,el in enumerate(args):
            try:
                args[i] = readfile(el)
            except:
                pass
        if len(args)> 0 and len(args[0].strip()) > 0:
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

        scriptContext = {"_C":scr,"self":self, "tools": self.tools}
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