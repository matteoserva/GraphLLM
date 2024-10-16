#
from .node_other import *
from .node_llm import *
from .node_agent import *
from .node_tools import *
from .node_inputs import *
from .node_exec import *
from ..logging.logger import Logger

def default_logger(*args,**kwargs):
    print(*args,**kwargs)

class ExecutorFactory:
    
    @staticmethod
    def makeExecutor(type="stateless",config={}):
        from ..graph.graph_executor import GraphExecutor
        full_config = {}
        full_config["name"] = config.get("name","/")
        full_config["logger"] = config.get("logger",Logger())
        full_config["client"] = config.get("client",None)
        full_config["path"] = config.get("path","/")

        executor=None
        if type == "stateless":
            executor = StatelessExecutor(full_config)
        elif type == "stateful":
            executor = StatefulExecutor(full_config)
        elif type == "constant":
            executor = ConstantNode()
        elif type == "agent":
            executor = AgentController(full_config)
        elif type == "tool":
            executor = ToolExecutor()
        elif type == "list":
            executor = ListNode()
        elif type == "copy":
            executor = CopyNode()
        elif type == "memory":
            executor = MemoryNode()
        elif type == "variable":
            executor = VariableNode()
        elif type == "graph":
            executor = GraphExecutor(full_config)
        elif type == "python":
            executor = PythonExecutor(full_config)
        elif type == "llamatool":
            executor = LlamaTool()
        elif type == "client":
            executor = Client()
        elif type == "user":
            executor = UserInputNode()
        elif type == "exec":
            executor = ExecNode()
        elif type == "file":
            executor = FileNode()

        executor.graph = config.get("graph",None)
        return executor
