import inspect

class AgentAnswer():
	def answer(self, computed_answer):
		"""outputs the answer to the user request."""
		print ("-------------",computed_answer)
		return "Operation complete"

class AgentMath():
	def sum(self, a,b):
		"""sums two numbers."""
		return a+b

	def neg(self, a):
		"""calculates the negated value of the argument."""
		return -a

	def mul(self, a,b):
		"""multiplies the two arguments."""
		return a*b

import random
import string
class AgentMath2():
	def __init__(self):
		self.cache={}

	def _make_random_name(self):
		r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		while r in self.cache:
			r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		return r

	def _parse_inputs(self,text_params):
		params = [el.split("=")[-1].strip() for el in text_params.split(",")]
		p2 = []
		for el in params:

			if el in self.cache:
				p2.append(self.cache[el])
			elif int(el) > 20:
				raise Exception("Variable " + el + " not found")
			else:
				p2.append(int(el))
		params = p2
		return params

	def sum(self, a,b):
		"""sums two numbers."""
		res = a+b
		r = self._make_random_name()
		self.cache[r] = res
		return "Result saved in variable " + r

	def neg(self, a):
		"""calculates the negated value of the argument."""
		return -a

	def mul(self, a, b):
		"""multiplies two arguments."""
		res = a*b
		r = self._make_random_name()
		self.cache[r] = res
		if True or res == 1024:
			return "Result saved in variable " + r
		return res

	def answer(self, computed_answer):
		"""outputs the answer to the user request."""
		print ("-------------",computed_answer)
		return computed_answer

from ast import literal_eval

class AgentOps():
	def __init__(self,*args):
		print("inizio")
		self.tools = {}
		self.add_tool(AgentMath2())
		#self.add_tool(AgentAnswer())

	def prepare(self,args):
		pass

	def add_tool(self, tool):
		ops = [el for el in dir(tool) if not el.startswith("_") ]
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
			row = row + " Parameters: " + params_string
			textlist.append(row)
		res = "\n".join(textlist)
		return res

	def exec(self, fname, text_params):
		if fname not in self.tools:
			raise Exception("The requested operation, " + fname + ", doesn't exist")
		row = self.tools[fname]
		tool = row["tool"]

		if "_parse_inputs" in dir(tool):
			params = tool._parse_inputs(text_params)
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
		try:
			res = self.exec(fname,text_params)
		except Exception as e:
			return e

		return res


import json
if __name__ == "__main__":
	a = AgentOps()
	ops = a.get_ops()
	#print(json.dumps(ops,indent=4))
	print(a.get_formatted_ops())
