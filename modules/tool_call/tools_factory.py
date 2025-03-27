import os
from glob import glob
from .common import GenericTool
from importlib import import_module
import sys, inspect
from functools import partial

_available_tools = None
def _load_available_tools():
    global _available_tools
    module_path = os.path.relpath(os.path.dirname(__file__)) # modules/executors
    module_name = __name__  # modules.executors
    base_module = ".".join(module_name.split(".")[:-1])
    sub_path = module_path
    # now locates all classes
    modules = [el[len(sub_path) + 1:-3] for el in glob(sub_path + "/*.py")]
    modules = [base_module + "." + el for el in modules if el.startswith("tool_")]
    found_classes = []
    for m in modules:
        try:
            module = import_module(m)
            attributes = [getattr(module, attribute_name) for attribute_name in dir(module)]
            generic_executors = [attribute for attribute in attributes if inspect.isclass(attribute)]
            found_classes.extend(generic_executors)
        except Exception as e:
            print("Exception while loading module",m, " : ", e,file=sys.stderr)
    found_tools = [el for el in found_classes if issubclass(el, GenericTool) and hasattr(el,"tool_name")]

    _available_tools = []
    for tool in found_tools:
        ops = [el for el in dir(tool) if not el.startswith("_")]
        is_default = tool.properties["default"] if hasattr(tool, "properties") and "default" in tool.properties else True
        tool_object = tool()
        tool_info = {"name": tool.tool_name, "class":tool, "operators": [], "default": is_default}

        for op in ops:

            c = getattr(tool_object, op)
            if not c:
                continue
            if not callable(c):
                continue
            d = inspect.getfullargspec(c)
            params = d[0][1:]
            e = len(params)

            params = [{"name": el} for el in params]
            row = {}
            row["name"] = op
            row["params"] = params
            row["doc"] = c.__doc__

            tool_info["operators"].append(row)

        _available_tools.append(tool_info)

class ToolRunner():
    def __init__(self,tools_list, node_graph_parameters):
        self.ops = {}
        tool_names = [el for el in tools_list]
        for tool_name in tools_list:
            tool_info = [el for el in _available_tools if el["name"] == tool_name][0]
            tool_object = tool_info["class"]()

            if len(node_graph_parameters.keys()) > 0:
                tool_object.path = node_graph_parameters.get("path", "/")
                tool_object.logger = node_graph_parameters.get("logger", None)
                tool_object.logger_print = partial(tool_object.logger.log, "print", tool_object.path)
            else:
                tool_object.logger_print = print

            for op in tool_info["operators"]:
                row = {name:op[name] for name in op}

                row["function"] = getattr(tool_object,op["name"])
                row["tool"] = tool_object
                self.ops[op["name"]] = row



    def get_formatted_ops(self):
        ops = [self.ops[el] for el in self.ops]
        textlist = []
        for op in ops:
            row = ""
            row = row + "- " + op["name"]
            if op["doc"] is not None:
                row = row + ": " + op["doc"]
            param_names = [el["name"] for el in op["params"]]
            params_string = ",".join(param_names)
            if row[-1] == ".":
                row = row[:-1]
            row = row + ". Parameters: " + params_string
            textlist.append(row)
        res = "\n".join(textlist)
        return res

    def _exec_name_list(self, function_name, function_parameters):
        op_info = self.ops[function_name]
        result = op_info["function"](*function_parameters)
        return result

    def _exec_name_dict(self, function_name, named_parameters):
        op_info = self.ops[function_name]
        result = op_info["function"](**named_parameters)
        return result

    def exec(self,*args,**kwargs):
        result = ""
        if len(args) == 2 and isinstance(args[0],str) and isinstance(args[1],list):
            result = self._exec_name_list(args[0],args[1])
        if len(args) == 1 and isinstance(args[0],str) and len(kwargs) > 0:
            result = self._exec_name_dict(args[0],kwargs)
        return result

class ToolsFactory():
    def __init__(self):
        if not _available_tools:
            _load_available_tools()

    def get_tool_classes(self, only_default=True):
        tools_list = [el["name"] for el in _available_tools if el["default"] or not only_default]
        return tools_list

    def get_operators(self, tool_classes):
        selected_tools = [el for el in available_tools if el["name"] in tool_classes]
        operators = [op for el in selected_tools for op in el["operators"]]
        return operators

    def make_tool_runner(self,tools_list, node_graph_parameters={}):
        tool_runner = ToolRunner(tools_list,node_graph_parameters)
        return tool_runner