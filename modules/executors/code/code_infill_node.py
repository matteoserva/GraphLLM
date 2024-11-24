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

        context_files.extend(fim_files)
        self.last_file_content = ""+context_files[-1][1]
        for el in fim_files:
            content = el[1]
            el[1] = "<|fim_prefix|>" + content.replace("{p:fim}","<|fim_suffix|>") + "<|fim_middle|>"
        context_list = ["<|file_sep|>" + el[0] + "\n" + el[1] for el in context_files]
        full_prompt = "<|repo_name|>" + self.repo_name + "\n" + "\n".join(context_list)
        self.full_prompt  = full_prompt

    def __call__(self,prompt_args):

        if self.properties.get("free_runs",0) > 0:
            self.properties["free_runs"] = 0
        if len(prompt_args) > 0:
            file_content = self.last_file_content
            if("{p:fim}" in file_content):
                file_content =file_content.replace("{p:fim}",prompt_args[0])
            else:
                file_content = file_content + prompt_args[0]


            res = [None,file_content]
        else:
            res = [self.full_prompt]
        return res