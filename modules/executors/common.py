from .gui_node_builder import GuiNodeBuilder
from modules.common.prompt_utils import solve_placeholders, solve_prompt_args

class ExecutorOutput():
    def __init__(self,data,meta={}):
        self.data = data
        self.meta = meta

    def __str__(self):
        return str(self.data)

class GenericExecutor():
    def __init__(self, initial_parameters):
        """ initialize, set_parameters(conf) - set_dependencies(deps) - set_template(init) - setup_complete - execute"""
        pass

    def get_properties(self):
        return self.properties

    def initialize(self, *args,**kwargs):
        pass

    def set_parameters(self, *args, **kwargs):
        conf = args[0]
        for el in conf:
            self.properties[el] = conf[el]

    def set_dependencies(self, *args, **kwargs):
        pass

    def set_template(self, init_args, *args,**kwargs):
        pass

    def setup_complete(self, *args, **kwargs):
        pass

    def graph_started(self):
        pass
        
    def graph_stopped(self):
        pass

    def __call__(self, inputs, *args):
        outputs = inputs
        return outputs

    def __getattr__(self,name):
        return getattr(self.node,name)


class BaseGuiParser:
    node_types = []

    def _make_default_config(self,old_config):
        new_config = {}
        new_config["type"] = old_config["type"].split("/")[-1]

        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        new_config["conf"] = old_config["properties"]

        return new_config

    def _calc_exec(self ,old_inputs ):

        new_inputs = old_inputs
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []

        max_arg_pos = -1
        for arg_pos, vel in enumerate(new_inputs):
            if vel:
                max_arg_pos = arg_pos
            val_exec.append(vel)
        if max_arg_pos > 0:
            val_exec = val_exec[:max_arg_pos+1]
        return val_exec

    def parse_node(self,old_config):
        new_config = self._make_default_config(old_config)
        return new_config

    def postprocess_nodes(self,new_nodes):
        pass


class BaseGuiNode(GuiNodeBuilder):

    def buildNode(self):
        builder = self._initBuilder()
        return builder

