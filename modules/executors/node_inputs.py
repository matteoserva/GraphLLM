
from ..common import get_input
from ..parser import solve_templates
from .common import solve_placeholders
from .common import GenericExecutor

class UserInputNode(GenericExecutor):
    node_type = "user"
    def __init__(self,*args):
        self.current_prompt = "{}"

    def get_properties(self):
        res = {"input_rule":"OR"}
        return res

    def set_template(self,args):
        cl_args = args
        if len(cl_args) > 0:
            self.current_prompt,_ = solve_templates(cl_args[0],cl_args[1:])


    def __call__(self,*args):
        try:
            while self.current_prompt.count("{}") > 0:
                m = [get_input() ]
                self.current_prompt , _ = solve_templates(self.current_prompt,m)
        except EOFError:
            return [None]
        new_prompt = self.current_prompt
        self.current_prompt = "{}"

        return new_prompt
    
class ListNode(GenericExecutor):
    node_type = "list"
    def __init__(self,*args):
        self.free_runs = 0
        self.current_iteration = 0

    def get_properties(self):
        res = {"free_runs":self.free_runs}
        return res

    def set_template(self,args):
        self.base_retval = args
        if not isinstance(args[0],list):
            self.base_retval = [[el] for el in args]
        self.retval = [[] for el in args]

    def __call__(self,args0, *prompt_args):


        if self.current_iteration == 0:
            for i,el in enumerate(self.base_retval):
                self.retval[i] = el
                self.retval[i][0] = solve_placeholders(el[0], args0)

        ret = self.retval[self.current_iteration]

        if not isinstance(ret,list):
            ret = [ret]
        ret[0], _ = solve_templates(ret[0], args0)

        #print(self.retval[self.current_iteration])

        self.current_iteration = (self.current_iteration + 1) % len(self.retval)
        if self.free_runs > 0:
            self.free_runs -= 1
        else:
            self.free_runs = len(self.retval) -1
        return ret
    
class ConstantNode(ListNode):
    node_type = "constant"
    def __init__(self,*args):
        super().__init__(*args)

    def load_config(self,args):
        super().load_config([args])