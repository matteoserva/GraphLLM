import json

class SequenceExecutor:
    def __init__(self,client):

        self.execRow = StatelessExecutor(client)
        self.client_parameters = None

    def set_client_parameters(self,p):
        self.execRow.set_client_parameters(p)

    def load_config(self,cl_args=None):
        cl_args[0] = try_solve_files([cl_args[0]])[0]
        for el in cl_args[1:]:
            cl_args[0] = cl_args[0].replace("{}",el,1)
        self.instructions_raw = cl_args[0]
        return cl_args

    def _execute_row(self,inputs,variables={}):
        for i in range(len(inputs)):
            try:
                p=readfile(inputs[i])
                inputs[i] = p
            except:
                pass
        m,_ = solve_templates(inputs[0],inputs[1:],variables)
        res = self.execRow([m])
        return res

    def _execute_list(self,instructions, cl_args):
        pos = 1
        variables={}
        res = None
        var_c = ["base"]*(1+len(cl_args))
        var_r = ["base"]*(1+len(instructions))
        for i,v in enumerate(cl_args):
            idx = i+1
            var_c[idx] = v
            stri = "c" + str(idx)
            variables[stri] = v
        variables["c"] = var_c
        variables["r"] = var_r
        for instr in instructions:
            res = self._execute_row(instr,variables)
            fn = "/tmp/llm_exec_" + str(pos) + ".txt"
            f = open(fn,"w")
            f.write(res)
            f.close()
            variables[str(pos)] = res
            var_r[pos] = res
            var_r[0] = res #pos 0 contiene sempre l'ultima
            pos = pos + 1
        return res

    def __call__(self,prompt):
        # for i,el in enumerate(prompt):
        #     try:
        #         prompt[i] = readfile(el)
        #     except:
        #         pass
        lista_istruzioni = self.instructions_raw
        instructions = [ [ es  for es in el.strip().split(" ") if len(es) > 0] for el in lista_istruzioni.strip().split("\n") if not el.startswith("#")]
        res = self._execute_list(instructions, prompt)
        return res


class CopyNode:
    def __init__(self,*args):
        self.parameters = {}
        self._properties = {"input_rule":"AND"}
        self._subtype="copy"
        self.stack = []
        self.cache = None

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

        self.parameters = args

    def _json_parse(self,text):
        r2 = text.find("{")
        decoder = json.JSONDecoder()
        val = decoder.raw_decode(text, r2)
        if isinstance(val,tuple):
            val = list(val)
            val = val[0]
        return val

    def __call__(self,*args):

        res = list(*args)
        if self._subtype  == "cast":
            res[0] = str(res[0])
        elif self._subtype == "repeat":
            if self.cache is None:
                self.cache = res
                self._properties["free_runs"] = 1
            else:
                res = self.cache
            
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
                if res[0] == "{p:eos}":
                    res = [self.stack]
                    self.stack = []
                else:
                    self.stack.append(res[0])
                    res = [None]
            else: #mux nello spazio
                l = [el for el in res if el is not None] #TODO: solo uno e mettere da parte gli altri
                res = l
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