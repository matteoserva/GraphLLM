#from .all_ops import *
from functools import partial

class AgentOps():
	def __init__(self,node_graph_parameters={}, *args):
		self.path = node_graph_parameters.get("path","/")
		self.logger = node_graph_parameters.get("logger",None)
		self.logger_print = partial(self.logger.log,"print",self.path)
		#self.logger_print("inizio")
		self.tools = {}
		self.add_tool(AgentMath2())
		#self.add_tool(AgentAnswer())

	def prepare(self,args):
		if len(args) > 0:
			self.tools = {}
		for el in args["tools"]:
			if el.lower() == "math":
				self.add_tool(AgentMath2())
			if el.lower() == "filesystem":
				self.add_tool(AgentFilesystem())
				pass
			if el.lower() == "llm":
				self.add_tool(AgentLLM())
				pass
			if el.lower() == "util":
				self.add_tool(AgentUtil())
			if el.lower() == "web":
				self.add_tool(AgentWeb())



	def add_tool(self, tool):
		ops = [el for el in dir(tool) if not el.startswith("_") ]
		tool.logger_print = self.logger_print
		for op in ops:
			c = getattr(tool,op)
			if not c:
				continue
			d = inspect.signature(c)
			e = len(d.parameters)
			params = list(d.parameters.keys())
			
			row ={}
			row["name"] = op	
			row["num_parameters"] = e
			row["params"] = params
			row["doc"] = c.__doc__
			row["function"] = c
			row["tool"] = tool
			self.tools[op] = row
	
	def get_ops(self):
		return self.tools.values()

	def get_formatted_ops(self):
		ops = self.get_ops()
		textlist = []
		for el in ops:
			row = ""
			row = row + "- " + el["name"]
			if el["doc"] is not None:
				row = row  + ": " + el["doc"]
			params_string = ",".join(el["params"])
			if row[-1] == ".":
				row = row[:-1]
			row = row + ". Parameters: " + params_string
			textlist.append(row)
		res = "\n".join(textlist)
		return res

	def exec(self, fname, text_params):
		if fname not in self.tools:
			raise Exception("The requested operation, " + fname + ", doesn't exist")
		row = self.tools[fname]
		tool = row["tool"]

		# se i parametri sono già separati allora li rimetto insieme. soluzione temporanea
		orig_params = text_params
		if isinstance(text_params,list):
			text_params = ",".join(text_params)

		if "_parse_inputs" in dir(tool):
			try:
				params,kp = tool._parse_inputs(fname,orig_params)
			except:
				params, kp = tool._parse_inputs(fname, text_params)
			if len(kp) > 0:
				av_params = [el for el in row["params"] if el in kp]
				data_params = [kp[el] for el in av_params]
				params.extend(data_params)
		else:
			if "cache" in dir(tool):
				params = [el.strip() for el in text_params.split(",")]
				params = [str(tool.cache[el]) if el in tool.cache else el for el in params]
				text_params = ",".join(params)
			try:
				params = literal_eval(text_params)
			except:
				raise Exception("error, the parameters must be in the correct format.")
			if isinstance(params,tuple):
				params=list(params)
			if not isinstance(params,list):
				params = [params]


		l1 = row["num_parameters"]
		l2 = len(params)
		if l1 != l2:
			raise Exception("The tool accepts " + str(l1) + " operands but " +str(l2) + " have been provided")
		f = row["function"]
		res = f(*params)
		return res

	def __call__(self, fname, text_params=None):
		if isinstance(fname,list) and text_params is None: #[{comando parametri}] oppure #[comando,param1,param2]
			if(len(fname) > 1):
				text_params = ",".join(fname[1:])
			fname = fname [0]

		if isinstance(fname,str) and text_params is None and fname.find("(") > 0:
			spl = fname.split("(")
			fname = spl[0]
			text_params = spl[1][:-1]

		if isinstance(fname,dict):
			fname, text_params = fname["command"], fname["args"]

		if fname == "get_formatted_ops":
			return self.get_formatted_ops()

		try:
			res = self.exec(fname,text_params)
		except Exception as e:
			return e

		return res
