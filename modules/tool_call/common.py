import subprocess
from ast import literal_eval
import json

from modules.common.base_tool import BaseTool as GenericTool

class RunGraphMixin():
    def _run_graph(self, *args):
        fullargs = ["python3", "exec.py", "-j", "-k"]
        fullargs.extend(args)
        proc = subprocess.Popen(fullargs, stdout=subprocess.PIPE, text=True)
        ret = ""
        while True:
            line = proc.stdout.read(4)
            if not line:
                break
            ret += line
            self.logger_print(line, end="", flush=True)
        last_row = ret.rstrip().split("\n")[-1]
        v1 = json.loads(last_row)
        return v1

