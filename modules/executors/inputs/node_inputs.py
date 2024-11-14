
from modules.common import try_solve_files
from modules.parser import solve_templates
from modules.executors.common import solve_placeholders
from modules.executors.common import GenericExecutor
from .node_list import ListNode

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


    
