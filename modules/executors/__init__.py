import sys, inspect
from glob import glob
import os

from pkgutil import iter_modules
from importlib import import_module

from modules.executors.common import GenericExecutor, BaseGuiParser

def _get_all_submodules(node_class=GenericExecutor):
    sub_path = "modules/executors"
    modules = [el[len(sub_path) + 1:-3] for el in glob(sub_path + "/*.py") if not el.startswith("_")]

    for sub_name, sub_path in [(f.name, f.path) for f in os.scandir("modules/executors") if f.is_dir()]:
        sub_modules = [el[len(sub_path) + 1:-3] for el in glob(sub_path + "/*.py") if not el.startswith("_")]
        sub_modules = [sub_name + "." + el for el in sub_modules]
        modules.extend(sub_modules)
    modules = ["modules.executors." + el for el in modules]

    # now filter
    found_executors = []
    for m in modules:
        module = import_module(m)
        attributes = [getattr(module, attribute_name) for attribute_name in dir(module)]
        generic_executors = [attribute for attribute in attributes if
                             inspect.isclass(attribute) and issubclass(attribute, node_class)]
        found_executors.extend(generic_executors)


    return found_executors

def get_executors():
    #from modules.executors import *



    from modules.executors.agent.node_agent import AgentController
    from modules.executors.tools.node_tools import ToolExecutor, LlamaTool
    from ..graph.graph_executor import GraphExecutor

    found_executors = _get_all_submodules(GenericExecutor)
    found_executors = [el for el in found_executors if hasattr(el,"node_type")]
    executors_map = {el.node_type:el for el in found_executors }

    executors_map["agent"] = AgentController
    executors_map["tool"] = ToolExecutor
    executors_map["graph"] = GraphExecutor
    executors_map["llamatool"] = LlamaTool
    return executors_map
    
def get_gui_parsers():
    found_parsers = _get_all_submodules(BaseGuiParser)
    found_parsers = [el for el in found_parsers if hasattr(el,"node_types")]
    return found_parsers
    
    