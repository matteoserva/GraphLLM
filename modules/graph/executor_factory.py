
from modules.logging.logger import Logger
import sys, inspect
from modules.executors.common import GenericExecutor
from modules.executors.agent.node_agent import AgentController
from modules.executors.tools.node_tools import ToolExecutor, LlamaTool

def default_logger(*args,**kwargs):
    print(*args,**kwargs)

from pkgutil import iter_modules
from importlib import import_module

def find_submodules(modules, python_name = "modules.executors"):
    found_executors = []
    filtered_modules = [el for el in modules if not el.ispkg]
    for module_tuple in filtered_modules:

        submodule_name = "{}.{}".format(python_name, module_tuple.name)
        module = import_module(submodule_name)
        attributes = [getattr(module, attribute_name) for attribute_name in dir(module)]
        generic_executors = [attribute for attribute in attributes if inspect.isclass(attribute) and issubclass(attribute, GenericExecutor) and hasattr(attribute, "node_type")]
        found_executors.extend(generic_executors)
    return found_executors

def _load_executor_classes():
    from ..graph.graph_executor import GraphExecutor
    found_executors = []
    executors = import_module("modules.executors")
    toplevel_modules = [el for el in iter_modules(executors.__path__)]
    found_executors.extend(find_submodules(toplevel_modules))

    for module_tuple in [el for el in toplevel_modules if el.ispkg]:
        python_name = "modules.executors.{}".format(module_tuple.name)
        submodule = import_module(python_name)
        subdirs = [el for el in iter_modules(submodule.__path__)]
        found_executors.extend(find_submodules(subdirs, python_name))

    executors_map = {el.node_type:el for el in found_executors}

    executors_map["agent"] = AgentController
    executors_map["tool"] = ToolExecutor
    executors_map["graph"] = GraphExecutor
    executors_map["llamatool"] = LlamaTool
    return executors_map

_available_executors = None

class ExecutorFactory:
    
    @staticmethod
    def makeExecutor(type="stateless",config={}):
        global _available_executors
        if not _available_executors:
            _available_executors = _load_executor_classes()
        full_config = {}
        full_config["name"] = config.get("name","/")
        full_config["logger"] = config.get("logger",Logger())
        full_config["client"] = config.get("client",None)
        full_config["path"] = config.get("path","/")

        executor=None
        if type in _available_executors:
            executor = _available_executors[type](full_config)

        return executor
