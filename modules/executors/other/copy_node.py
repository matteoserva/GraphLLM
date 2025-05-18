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
        self.properties = {"input_rule":"AND"}
        self._subtype="copy"
        self.stack = []
        self.cache = None
        self.repeat_runs = 0
        self._demux_N = 2
        self._demux_i = 0

    def get_properties(self):
        res = self.properties
        return res

    def set_parameters(self,args):
        if "subtype" in args:
            self._subtype = args["subtype"]
            if args["subtype"] == "mux":
                self.properties["input_rule"] = "OR"
            if args["subtype"] == "gate":
                self.properties["input_rule"] = "XOR"
                self.properties["input_active"] = 0
            if args["subtype"] == "repeat":
                self.repeat_runs = args.get("repeat",0)
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
        if self._subtype == "input":
            self.node.disable_execution=True
        elif self._subtype  == "cast":
            res[0] = str(res[0])
        elif self._subtype == "repeat":
            if self.cache is None:
                self.cache = res
                self.properties["free_runs"] = self.repeat_runs - 1 if self.repeat_runs > 1 else 0
            else:
                res = self.cache

            if self.repeat_runs == 0: #infinite
                self.properties["free_runs"] = 1

            if self.properties["free_runs"] == 0:
                self.cache = None

        elif self._subtype == "gate":
            numInputs = len(res)
            outval = [None] * numInputs
            input_active = self.properties["input_active"]
            outval[input_active] = res[input_active]
            input_active = (input_active + 1) % numInputs

            self.properties["input_active"] = input_active
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

                l = [(idx,el) for idx,el in enumerate(res) if el is not None][0] #TODO: solo uno e mettere da parte gli altri
                res = [l[1],l[0]]

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

        elif self._subtype == "unpack" and len(self.node.outputs) == 1:
            if len(self.stack) == 0:
                self.stack = res[0][::-1]
            val = self.stack.pop()
            res = [val]
            self.properties["free_runs"] = 1 if len(self.stack) > 0 else 0

        elif self._subtype == "pack" and len(self.node.inputs) > 1:
            val = res
            res = [val]



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

