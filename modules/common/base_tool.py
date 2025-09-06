
class BaseTool():
	def __init__(self):
		pass

	def _parse_inputs(self,fname, text_params):
		if isinstance(text_params,list):
			return text_params,{}
		val = """def args_to_dict(*args,**kwargs):\n  return args,kwargs\nres = args_to_dict({})\n"""
		ex = val.format(text_params)
		l = {}
		exec(ex, l, l)
		a,k = l["res"]
		b=list(a)
		return b,k