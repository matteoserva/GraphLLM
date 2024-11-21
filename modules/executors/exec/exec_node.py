import copy
import subprocess

from modules.executors.common import GenericExecutor

class ExecNode(GenericExecutor):
    node_type = "exec"
    def __init__(self,*args):
        pass

    def set_template(self,args):
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