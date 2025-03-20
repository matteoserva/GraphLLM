import subprocess
from ast import literal_eval
import json


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

class GenericTool():
	def __init__(self):
		pass



	def _parse_inputs(self,fname, text_params):
		if isinstance(text_params,list):
			return text_params,{}
		val = """def args_to_dict(*args,**kwargs):\n  return args,kwargs\nres = args_to_dict({})\n"""
		ex = val.format(text_params)
		l = {}
		exec(ex, l, l)
		a,k = l["res"]
		b=list(a)
		return b,k

