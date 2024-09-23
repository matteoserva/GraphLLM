from .main_ops import AgentOps

if __name__ == "__main__":
	a = AgentOps()
	ops = a.get_ops()
	#print(json.dumps(ops,indent=4))
	print(a.get_formatted_ops())