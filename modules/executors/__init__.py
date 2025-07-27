import sys, inspect
from glob import glob
import os

from pkgutil import iter_modules
from importlib import import_module

from modules.common.base_executor import BaseExecutor
from modules.executors.common import BaseGuiParser, BaseGuiNode

_search_directories = [os.path.dirname(__file__), os.path.dirname(__file__) + "/../custom_nodes"]
_class_cache = None

def _search_classes(folder):

    # retrieves the name and location of this file
    module_path = os.path.relpath(folder) # modules/executors
    #module_name = __name__  # modules.executors

    module_name = module_path.replace("/",".")
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

    # filter imported classes
    found_classes = [el for el in found_classes if el.__module__.startswith(module_name)]

    return found_classes

def _load_classes(search_directories):
    global _class_cache
    if _class_cache is None:
        found_classes = [el for _dir in search_directories for el in _search_classes(_dir)]
        found_classes = list(dict.fromkeys(found_classes))
        _class_cache = found_classes
    return _class_cache

def _get_all_submodules(node_class=BaseExecutor):

    found_classes = _load_classes(_search_directories)

    # now filter
    found_executors = [el for el in found_classes if issubclass(el, node_class) ]

    return found_executors

def get_executors():

    from modules.executors.agent.agent_node import AgentController
    from modules.executors.utils.node_tools import ToolExecutor, LlamaTool
    from ..graph.graph_executor import GraphExecutor

    found_executors = _get_all_submodules(BaseExecutor)
    found_executors = [el for el in found_executors if hasattr(el,"node_type")]
    executors_map = {el.node_type:el for el in found_executors }

    executors_map["agent"] = AgentController
    executors_map["tool"] = ToolExecutor
    #executors_map["graph"] = GraphExecutor
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
    