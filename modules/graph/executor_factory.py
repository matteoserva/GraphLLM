
from modules.logging.logger import Logger
import sys, inspect
from glob import glob
import os

from modules.executors import *
from modules.executors.common import GenericExecutor
from modules.executors.agent.node_agent import AgentController
from modules.executors.tools.node_tools import ToolExecutor, LlamaTool

def default_logger(*args,**kwargs):
    print(*args,**kwargs)

from pkgutil import iter_modules
from importlib import import_module

def _load_executor_classes():
    from ..graph.graph_executor import GraphExecutor
    modules = [el[:-3] for el in glob("*.py",root_dir="modules/executors" ) if not el.startswith("_")]

    for sub_name, sub_path in [ (f.name, f.path) for f in os.scandir("modules/executors") if f.is_dir()]:
        sub_modules = [el[:-3] for el in glob("*.py",root_dir=sub_path ) if not el.startswith("_")]
        sub_modules = [sub_name + "." + el for el in sub_modules]
        modules.extend(sub_modules)
    modules = ["modules.executors." + el for el in modules]

    found_executors = []
    for m in modules:
        module = import_module(m)
        attributes = [getattr(module, attribute_name) for attribute_name in dir(module)]
        generic_executors = [attribute for attribute in attributes if
                             inspect.isclass(attribute) and issubclass(attribute, GenericExecutor) and hasattr(attribute, "node_type")]
        found_executors.extend(generic_executors)


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
