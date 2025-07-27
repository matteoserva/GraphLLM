
class BaseExecutor():
    def __init__(self, initial_parameters):
        """ initialize, set_parameters(conf) - set_dependencies(deps) - set_template(init) - setup_complete - execute"""
        pass

    def get_properties(self):
        return self.properties

    def initialize(self, *args, **kwargs):
        pass

    def set_parameters(self, *args, **kwargs):
        conf = args[0]
        for el in conf:
            self.properties[el] = conf[el]

    def set_dependencies(self, *args, **kwargs):
        pass

    def set_template(self, init_args, *args, **kwargs):
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

    def __getattr__(self, name):
        return getattr(self.node, name)