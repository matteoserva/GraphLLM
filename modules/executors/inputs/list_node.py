from modules.common import try_solve_files
from modules.parser import solve_templates
from modules.executors.common import solve_placeholders
from modules.executors.common import GenericExecutor


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