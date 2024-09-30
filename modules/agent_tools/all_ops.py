import inspect
import subprocess
import os
import random
import string
from ast import literal_eval
from .common import *
from ..common import PythonInterpreter
import json

class AgentUtil(GenericAgent):
	def __init__(self):
		pass

	def eval(self,expression):
		"""Evaluates a python expression and returns the result."""
		val = eval(expression)
		return val

	def python_exec(self, python_code):
		"""Executes python code. The argument is a multiline string containing the code to be executed."""
		interpreter = PythonInterpreter()
		res = interpreter.execute(python_code,{})
#		if len(res) == 0:
#			res="Exception: no output returned. Did you forget to call print()?"
		return res


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
		#result = subprocess.run(fullargs, capture_output=True, text=True, input="")
		return "Webpage at url " + url + " successfully saved at /tmp/pagina.md"

	def web_search(self,query):
		"""performs a web search using a search engine."""
		modified_query = query.replace(" ","+")
		search_url = "https://lite.duckduckgo.com/lite/?q=" + modified_query + ""
		self.download(search_url)
		fullargs = ["python3", "exec.py", "graphs/run_template.txt","templates/extract_search_results.txt","/tmp/pagina.md","5"]
		result = subprocess.run(fullargs, capture_output=True, text=True, input="")
		last_row = result.stdout.strip().split("\n")[-1]
		v1 = json.loads(last_row)
		v2 = v1[0]

		return v2

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

	def query_file(self,filename, question):
		"""Uses a external agent to answer a {question} about the file saved in {filename}."""
		val = self._run_graph("graphs/file_question.txt",filename,question)
		return val
		
	def _query_information(self, question):
		"""Queries a external agent to obtain information about everything."""
		val = ""
		return val

	def summarize(self,filename):
		"""Uses a external agent to generate a plain-text summary of the content of a file."""
		val = self._run_graph("graphs/run_template.txt","templates/summarize_full.txt",filename)
		with open("/tmp/summary.txt","w") as f:
			f.write(val)

		res = f"Summary of {filename} successfully generated and saved in /tmp/summary.txt"
		if len(val) < 1024:
			res = res + "\n\n" + val
		return res



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
			return f"file {file_name} is too large for read(). You should use the query_file() tool to query its content if the tool is available."
		with open(file_name,"r") as f:
			content = f.read()
		return content

	def answer_file(self, file_name):
		"""Returns a file as answer for the user question. This is the preferred way for returning an answer to the user."""
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
