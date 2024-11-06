
from modules.common import try_solve_files
from modules.parser import solve_templates
from modules.executors.common import solve_placeholders
from modules.executors.common import GenericExecutor


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
                m = [self._get_input() ]
                self.current_prompt , _ = solve_templates(self.current_prompt,m)
        except EOFError:
            return [None]
        new_prompt = self.current_prompt
        self.current_prompt = "{}"

        return new_prompt

    def _get_input_simple(self, inprompt="> "):
        prompt = self.api.get_user_input(inprompt)
        prompt_full = ""
        if len(prompt) > 0 and prompt[-1] == "\\":
            while len(prompt) > 0 and prompt[-1] == "\\":
                prompt = prompt[0:len(prompt) - 1] + "\n"
                prompt_full = prompt_full + prompt
                prompt = self.api.get_user_input(". ")
            prompt_full = prompt_full + prompt
        elif len(prompt) == 3 and prompt == "'''":
            prompt = self.api.get_user_input(". ")
            while len(prompt) != 3 or prompt != "'''":
                prompt_full = prompt_full + "\n" + prompt
                prompt = self.api.get_user_input(". ")
            prompt_full = prompt_full[1:]
        else:
            prompt_full = prompt_full + prompt

        return prompt_full

    # tries to solve templates from the args stack. then it asks the user
    def _get_input(self, prompt_full="{}", args_stack=[]):
        inprompt = "> "
        if (prompt_full != "{}"):
            inprompt = "! "
        while True:
            prompt_full, need_more = solve_templates(prompt_full, args_stack)
            args_stack = []
            if not need_more:
                break
            prompt = self._get_input_simple(inprompt)
            inprompt = "! "
            prompt_full = prompt_full.replace("{}", prompt, 1)

        return prompt_full

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

    def set_template(self,args):
        solved_args = try_solve_files(args)
        packed_args = [solved_args]
        super().set_template(packed_args)
