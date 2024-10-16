from ..parser import solve_templates

class GenericExecutor:
    def __init__(self, initial_parameters):
        """ initialize, conf - deps - init - """
        pass

    def initialize(self, *args,**kwargs):
        pass

    def set_parameters(self, *args, **kwargs):
        pass

    def set_dependencies(self, *args, **kwargs):
        pass

    def set_template(self, init_args, *args,**kwargs):
        new_init_args = []
        for i, v in enumerate(init_args):
            if v == "{v:c*}":
                new_init_args.extend(self.graph.variables["c*"])
            else:
                new_init_args.append(v)
        init_args = new_init_args
        for i, v in enumerate(init_args):
            init_args[i], _ = solve_templates(init_args[i], [], self.graph.variables)
        if hasattr(self,"load_config"):
            self.load_config(init_args)

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
