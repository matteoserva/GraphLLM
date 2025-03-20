from .common import GenericTool

class AgentMath2(GenericTool):
    #tool_name = "simple_math"
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
		print_agent_answer (computed_answer)
		return computed_answer