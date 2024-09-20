import inspect
import subprocess
import os

class AgentAnswer():
	def answer(self, computed_answer):
		"""outputs the answer to the user request."""
		print ("-------------",computed_answer)
		return "Operation complete"

import random
import string

class GenericAgent():
	def __init__(self):
		pass

	def _parse_inputs(self,fname, text_params):
		val = """def args_to_dict(*args,**kwargs):\n  return args,kwargs\nres = args_to_dict({})\n"""
		ex = val.format(text_params)
		l = {}
		exec(ex, l, l)
		a,k = l["res"]
		b=list(a)
		return b,k


	def answer(self, computed_answer):
		"""outputs the answer to the user request."""
		print ("-------------",computed_answer)
		return computed_answer

class AgentUtil(GenericAgent):
	def __init__(self):
		pass

	def eval(self,expression):
		"""Evaluates a mathematical expression in python notation and returns the result."""
		val = eval(expression)
		return val

class AgentWeb(GenericAgent):
	def __init__(self):
		pass

	def eval(self,expression):
		"""Evaluates a mathematical expression in python notation and returns the result."""
		val = eval(expression)
		return val

	def download(self,url):
		"""Downloads the webpage at url {url} and saves its html content to a temporary file"""
		fullargs = ["python3", "../scraper/scrape.py", url]
		result = subprocess.run(fullargs, capture_output=True, text=True, input="")
		return "Webpage at url " + url + " successfully saved at /tmp/pagina.md"

class AgentLLM(GenericAgent):
	def __init__(self):
		pass

	def _run_graph(self,*args):
		fullargs = ["python3", "exec.py"]
		fullargs.extend(args)
		result = subprocess.run(fullargs, capture_output=True, text=True, input="")
		ret = str(result.stdout)
		val = ret.split("\n")[-2]
		val = literal_eval(val)[0]
		return val

	def ask(self,filename, question):
		"""Uses a external agent to answer a {question} about the file saved in {filename}."""
		val = self._run_graph("graphs/file_question.txt",filename,question)
		return val

	def summarize(self,filename):
		"""Uses a external agent to process a saved file {filename} and generate a summary of its content."""
		val = self._run_graph("graphs/run_template.txt","templates/summarize_full.txt",filename)
		with open("/tmp/summary.txt","w") as f:
			f.write(val)
		return f"Summary of {filename} successfully saved /tmp/summary.txt"



class AgentFilesystem(GenericAgent):
	def __init__(self):
		pass

	def ls(self,dirname):
		"""outputs the content of the directory dirname."""
		return ".\n..\nciao.txt\npagina.md"

	def read(self,file_name):
		"""Reads a file and outputs its content. This function fails if the file is too large."""
		if not file_name.startswith("/"):
			return "Error: You need to input a full path for the file_name"
		if not file_name.startswith("/tmp"):
			return "Error: You don't have access to that directory"
		file_stats = os.stat(file_name)
		file_size = file_stats.st_size

		if file_size > 2048:
			return f"file {file_name} is too large for read(). You should use the ask() tool to query its content if the tool is available."
		with open(file_name,"r") as f:
			content = f.read()
		return content

	def answerFile(self, file_name):
		"""Returns a file as answer for the user question."""
		with open(file_name,"r") as f:
			content = f.read()
		print ("-------------\n" + content)
		return "Answer sent to user"

class AgentMath2():
	def __init__(self):
		self.cache={}

	def _make_random_name(self):
		r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		while r in self.cache:
			r = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
		return r

	def _parse_inputs(self,fname, text_params):
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
		return params,{}

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
			params,kp = tool._parse_inputs(fname,text_params)
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
