from ..parser import solve_templates

# def metaclass_protect(*protected):
#     """Returns a metaclass that protects all attributes given as strings"""
#     class Protect(type):
#         has_base = False
#         def __new__(meta, name, bases, attrs):
#             if meta.has_base:
#                 for attribute in attrs:
#                     if attribute in protected:
#                         raise AttributeError('Overriding of attribute "%s" not allowed.'%attribute)
#             meta.has_base = True
#             klass = super().__new__(meta, name, bases, attrs)
#             return klass
#     return Protect

#metaclass=metaclass_protect("pre_initialize","set_template")

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

    def __getattr__(self,name):
        return getattr(self.node,name)


class BaseGuiParser:
    node_types = []

    def _calc_exec(self ,old_inputs ):

        new_inputs = old_inputs
        new_inputs = [str(el[1]) + "[" + str(el[2]) + "]" if el else None for el in new_inputs]
        val_exec = []
        for vel in new_inputs:
            if not vel:
                break
            val_exec.append(vel)
        return val_exec

    def parse_node(self,old_config):
        return None

    def postprocess_nodes(self,new_nodes):
        pass


def solve_placeholders(base, confArgs, confVariables={}):
        for i in range(len(confArgs)):
            name = "{p:exec" + str(i + 1) + "}"
            val = confArgs[i]
            base = base.replace(name, val)
        for el in confVariables:
            name = "{p:" + el + "}"
            val = confVariables[el]
            base = base.replace(name, val)
        return base





        
