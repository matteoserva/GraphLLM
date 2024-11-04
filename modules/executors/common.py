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

class ClientCallback:
    def __init__(self, print_response,logger_print):
        self.print_response = print_response
        self.logger_print = logger_print

    def __call__(self, line):
        if self.print_response:
            self.logger_print(line, end="", flush=True)

def send_chat(builder,client,client_parameters=None,print_response=True, logger_print=print):
    callback = ClientCallback(print_response,logger_print)
    ret = client.send_prompt(builder,params=client_parameters,callback = callback)
    if print_response and print_response != "partial":
        logger_print("")
    return ret

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


class BaseGuiParser:
    node_types = []
    def parse_node(self,old_config):
        return None

    def postprocess_nodes(self,new_nodes):
        pass


        
