from .common import GenericTool

def print_agent_answer(computed_answer):
	print("------------- agent answer:\n" + str(computed_answer))

class AgentAnswer(GenericTool):
	tool_name = "answer"
	properties = {"priority": 100}

	def answer(self, computed_answer):
		"""outputs the answer to the user request."""
		print_agent_answer (computed_answer)
		return computed_answer