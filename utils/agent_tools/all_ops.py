import inspect
import subprocess
import os
import random
import string
from ast import literal_eval

class AgentAnswer():
	def answer(self, computed_answer):
		"""outputs the answer to the user request."""
		print ("-------------",computed_answer)
		return "Operation complete"


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