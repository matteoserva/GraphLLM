from .common import GenericTool
from ..fake_python import PythonInterpreter

class AgentUtil(GenericTool):
    tool_name = "eval"

    def eval(self,expression):
        """Evaluates a python expression and returns the result."""
        val = eval(expression)
        return val

    def python_exec(self, python_code):
        """Executes python code. The argument is a multiline string containing the code to be executed."""
        interpreter = PythonInterpreter()
        res = interpreter.execute(python_code,{})
#		if len(res) == 0:
#			res="Exception: no output returned. Did you forget to call print()?"
        return res
