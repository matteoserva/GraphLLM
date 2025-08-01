import json
from modules.executors.common import GenericExecutor
from modules.executors.common import ExecutorOutput

class JsonNode(GenericExecutor):
    node_type = "json_parser"
    """
    Parses json data and indents the result
    """
    def __init__(self,*args):
        self.parameters = {}

    def __call__(self,*args):
        res = list(*args)
        text = res[0]
        try:
            val = json.loads(text)
        except:
            val = text
        valstring = json.dumps(val, indent=4).strip()
        outval = valstring
        out = [outval]
        return out
