from modules.executors.common import GenericExecutor
from modules.fake_python import PythonConsole
import sys

class PythonConsoleNode(GenericExecutor):
    node_type = "python_console"

    def initialize(self, *args,**kwargs):      
        self._interpreter = PythonConsole()
        
    def graph_started(self):
        self._interpreter.reset()

    def __call__(self, inputs, *args):
        user_prompt = inputs[0]
        retval = self._interpreter.push(user_prompt)
        
        outputs = [retval]
        return outputs