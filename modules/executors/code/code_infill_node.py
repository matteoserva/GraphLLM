from modules.executors.common import GenericExecutor
from modules.common import readfile

class CodeInfillNode(GenericExecutor):
    node_type = "code_infill"
    def __init__(self,node_graph_parameters):
        self.repo_name="test"
        self.file_names = ["main"]
        self.full_prompt = ""

    def initialize(self):
        pass

    def set_parameters(self, *args, **kwargs):
        conf = args[0]
        for el in conf:
            if el == "repo_name":
                self.repo_name = conf[el]
            elif el == "file_names":
                self.file_names = conf[el]
            else:
                self.properties[el] = conf[el]

    def set_template(self,cl_args=None):
        for i,el in enumerate(cl_args):
            try:
                cl_args[i] = readfile(el)
            except:
                pass

        context_files = []
        fim_files = []
        for name, content in zip(self.file_names, cl_args):
            if "{p:fim}" in content:
                fim_files.append([name,content])
            else:
                context_files.append((name,content))
        for el in fim_files:
            content = el[1]
            el[1] = "<|fim_prefix|>" + content.replace("{p:fim}","<|fim_suffix|>") + "<|fim_middle|>"
        context_files.extend(fim_files)
        context_list = ["<|file_sep|>" + el[0] + "\n" + el[1] for el in context_files]
        full_prompt = "<|repo_name|>" + self.repo_name + "\n" + "\n".join(context_list)
        self.full_prompt  = full_prompt

    def __call__(self,prompt_args):
        res = [self.full_prompt ]

        return res