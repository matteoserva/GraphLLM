import json
from modules.executors.common import GenericExecutor

class CopyNode(GenericExecutor):
    """
    no subtype: copy inputs to output
    gate: scan inputs and copy one at each iterations
    mux: if multiple inputs, take any. index is second output
    mux: in one onput, accumulate untile {p:eos} (second output is number of elements?)
    demux: take a input and index, fills the output at index
    repeat: repeats the input N times as specified in free_runs
    log: save to file (deprecated by filenode)
    """

    node_type = "copy"

    def __init__(self,*args):
        self.parameters = {}
        self._properties = {"input_rule":"AND"}
        self._subtype="copy"
        self.stack = []
        self.cache = None
        self.repeat_runs = 0
        self._demux_N = 2
        self._demux_i = 0

    def get_properties(self):
        res = self._properties
        return res

    def set_parameters(self,args):
        if "subtype" in args:
            self._subtype = args["subtype"]
            if args["subtype"] == "mux":
                self._properties["input_rule"] = "OR"
            if args["subtype"] == "gate":
                self._properties["input_rule"] = "XOR"
                self._properties["input_active"] = 0
            if args["subtype"] == "repeat":
                self.repeat_runs = args.get("free_runs",0)
        self.parameters = args

    def _json_parse(self,text):
        r2 = text.find("{")
        decoder = json.JSONDecoder()
        val = decoder.raw_decode(text, r2)
        if isinstance(val,tuple):
            val = list(val)
            val = val[0]
        return val
#il mux invia la posizione come secondo elemento
#il demux riceve la posizione come secondo elemento
# anche pack e unpack
    def __call__(self,*args):
        if "max_runs" in self.parameters:
            if self.parameters["max_runs"] > 0:
                self.parameters["max_runs"] = self.parameters["max_runs"] -1
            else:
                return [None]
        res = list(*args)
        if self._subtype  == "cast":
            res[0] = str(res[0])
        elif self._subtype == "repeat":
            if self.cache is None:
                self.cache = res
                self._properties["free_runs"] = self.repeat_runs -1
            else:
                res = self.cache
                if self._properties["free_runs"] > 0:
                    self._properties["free_runs"] = self._properties["free_runs"] - 1
                    if self._properties["free_runs"] == 0:
                        self.cache = None
            if self.repeat_runs == 0: #infinite
                self._properties["free_runs"] = 1

        elif self._subtype == "gate":
            numInputs = len(res)
            outval = [None] * numInputs
            input_active = self._properties["input_active"]
            outval[input_active] = res[input_active]
            input_active = (input_active + 1) % numInputs

            self._properties["input_active"] = input_active
            res = outval
        elif self._subtype == "mux":
            if len(res) == 1: #mux nel tempo
                if res[0] == "{p:eos}" and len(self.stack) > 0:
                    res = [self.stack]
                    self.stack = []
                else:
                    self.stack.append(res[0])
                    res = [None]
            else: #mux nello spazio
                l = [el for el in res if el is not None] #TODO: solo uno e mettere da parte gli altri
                res = l
        elif self._subtype == "demux":
            """ if the index is present, then use it, else alternate the outputs """
            if len(res) > 1:
                index = int(res[1])
            else:
                index = self._demux_i
            value = res[0]
            outval = [None] * (index+1)
            outval[index] = value
            self._demux_i = (self._demux_i + 1) % self._demux_N
            res = outval
        elif self._subtype == "log":
            if "logfile" in self.parameters:
              fn = self.parameters["logfile"]
              with open(fn,"w") as f:
                f.write(res[0])

        elif ("return_attr" in self.parameters):
            attr_name = self.parameters["return_attr"]
            v = res[0]
            base = self._json_parse(v)
            res[0] = base[attr_name]
        return res

class VariableNode(GenericExecutor):
    node_type = "variable"

    def __init__(self,*args):
        pass

    def initialize(self):
        pass

    def set_parameters(self, args):
        self.parameters = args
        conf = self.node.config["conf"]
        graph = self.node.graph
        variables = self.node.graph.variables
        name = conf["name"]
        value = conf["value"]
        if "[" in name:
            name, index = name.split("[",1)
            index = index.split("]")[0]
            if name not in variables:
                variables[name] = {}
            variables[name][index] = value


        else:
            variables[conf["name"]] = conf["value"]

    def __call__(self, *args):
        return []

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
                      f.write(args[0][0])
        try:
            with open(self.filename) as f:
                val = f.read()
        except FileNotFoundError:
            val = ""
        return val


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
