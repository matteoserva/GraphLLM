from modules.executors.common import GenericExecutor
from modules.fake_python import PythonConsole
import sys
from modules.tool_call.tools_factory import ToolsFactory

class PythonConsoleNode(GenericExecutor):
    node_type = "python_console"

    def __init__(self,*args):
        tools_factory = ToolsFactory()
        tools_list = tools_factory.get_tool_classes(only_default=False)
        tool_runner = tools_factory.make_tool_runner(tools_list, args[0])
        self.tools = tool_runner

    def initialize(self, *args,**kwargs):      
        self._interpreter = PythonConsole()
        
        
    def graph_started(self):
        scriptContext = {"self":self,"tools": self.tools}
        if self.properties.get("echo","NO") == "NO":
            echo = False
        else:
            echo = True
        s_strip = self.properties.get("strip","AUTO")
        if s_strip == "YES":
            strip = True
        elif s_strip == "NO":
            strip = False
        else:
            strip = None

        self._interpreter.reset(scriptContext)
        self._interpreter.setEchoMode(echo)
        self._interpreter.setPromptStrip(strip)

    def __call__(self, inputs, *args):
        user_prompt = inputs[0]
        retval = self._interpreter.push(user_prompt)
        
        outputs = [retval]
        return outputs