import json
from modules.executors.common import GenericExecutor


class MemoryNode(GenericExecutor):
    node_type = "memory"
    """
    outputs the accumulated inputs so far
    """
    def __init__(self,*args):
        self.parameters = {}
        self._properties = {"input_rule":"AND"}
        self._subtype="append"
        self._preprocessing="json"
        self._stack = []

    def get_properties(self):
        res = self._properties
        return res

    def set_parameters(self,args):
        self.parameters = args

    def _json_parse(self,text):
        val = None
        try:
            val = json.loads(text)
        except:
            val = json.loads("{" + text + "}")
        val = json.dumps(val, indent=4).strip()
        return val

    def __call__(self,*args):
        res = list(*args)
        try:
            val = self._json_parse(res[0])
            self._stack.append(val)
        except:
            self._stack.append(res[0])
        separator = self.parameters.get("separator","\n")
        outval = separator.join(self._stack)
        out = [outval]
        return out
