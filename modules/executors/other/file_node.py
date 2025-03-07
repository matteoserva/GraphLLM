import json
from modules.executors.common import GenericExecutor


class FileNode(GenericExecutor):
    node_type = "file"
    def __init__(self,*args):
        pass

    def set_template(self, args):
        self.filename = args[0]

    def __call__(self, *args):
        self.properties["free_runs"] = 0
        create = self.properties.get("create",False)
        write_mode = "w+" if create else "w"
        if len(args[0]) > 0:
             with open(self.filename,write_mode) as f:
                      f.write(str(args[0][0]))
        try:
            with open(self.filename) as f:
                val = f.read()
        except FileNotFoundError:
            val = ""
        return val