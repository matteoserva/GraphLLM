import json
from modules.executors.common import GenericExecutor


class JsonNode(GenericExecutor):
    node_type = "json_parser"
    """
    Parses json data and indents the result
    """
    def __init__(self,*args):
        self.parameters = {}


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
        except:
            val = res[0]

        out = [val]
        return out
