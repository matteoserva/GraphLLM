import sys, inspect
from glob import glob
import os

from pkgutil import iter_modules
from importlib import import_module

from modules.executors.common import GenericExecutor, BaseGuiParser, BaseGuiNode

_cached_classes = None

def _get_all_classes():
    global _cached_classes
    if _cached_classes:
        return _cached_classes

    # retrieves the name and location of this file
    module_path = os.path.relpath(os.path.dirname(__file__)) # modules/executors
    module_name = __name__  # modules.executors
    sub_path = module_path
    
    # now locates all classes
    modules = [el[len(sub_path) + 1:-3] for el in glob(sub_path + "/*.py") if not el.startswith("_")]

    for sub_name, sub_path in [(f.name, f.path) for f in os.scandir(module_path) if f.is_dir()]:
        sub_modules = [el[len(sub_path) + 1:-3] for el in glob(sub_path + "/*.py") if not el.startswith("_")]
        sub_modules = [sub_name + "." + el for el in sub_modules]
        modules.extend(sub_modules)
    modules = [module_name + "." + el for el in modules]

    found_classes = []
    for m in modules:
        try:
            module = import_module(m)
            attributes = [getattr(module, attribute_name) for attribute_name in dir(module)]
            generic_executors = [attribute for attribute in attributes if inspect.isclass(attribute)]
            found_classes.extend(generic_executors)
        except Exception as e:
            print("Exception while loading module",m, " : ", e,file=sys.stderr)

    _cached_classes = found_classes
    return found_classes

def _get_all_submodules(node_class=GenericExecutor):

    found_classes = _get_all_classes()
    # now filter
    found_executors = [el for el in found_classes if issubclass(el, node_class) ]

    return found_executors

def get_executors():
    #from modules.executors import *



    from modules.executors.agent.agent_node import AgentController
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
    found_parsers = [el for el in found_parsers if hasattr(el,"node_types") and len(el.node_types) > 0]
    return found_parsers

def get_gui_nodes():
    found_parsers = _get_all_submodules(BaseGuiNode)
    found_parsers = [el for el in found_parsers if el is not BaseGuiNode]
    return found_parsers
    