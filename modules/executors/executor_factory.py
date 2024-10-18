#
from .node_other import *
from .node_llm import *
from .node_agent import *
from .node_tools import *
from .node_inputs import *
from .node_exec import *
from ..logging.logger import Logger
import sys, inspect
from .common import GenericExecutor

def default_logger(*args,**kwargs):
    print(*args,**kwargs)

def _load_executor_classes():
    res = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    res = [el[1] for el in res if issubclass(el[1], GenericExecutor)]
    res = {el.node_type: el for el in res if hasattr(el, "node_type")}
    return res

_available_executors = _load_executor_classes()



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
        if type in _available_executors:
            executor = _available_executors[type](full_config)
        elif type == "agent":
            executor = AgentController(full_config)
        elif type == "tool":
            executor = ToolExecutor()
        elif type == "graph":
            executor = GraphExecutor(full_config)
        elif type == "llamatool":
            executor = LlamaTool()
        elif type == "client":
            executor = Client()
        return executor
