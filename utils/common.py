
from .formatter import Formatter
from .parser import solve_templates
import copy

from io import StringIO
from contextlib import redirect_stdout
import builtins

class PythonInterpreter:
    def __init__(self):
        self.whitelist = ["sum", "range", "int"]
        pass

    def fakeimport(self, name, *args,**kwargs):
        #print("fakeimport", name, args,kwargs)
        if name in ["sympy"]:
            return __import__(name)


    def execute(self,code, context):
        safe_builtins = {'print': print, 'dir': dir}
        for el in self.whitelist:
            safe_builtins[el] = getattr(builtins, el)
        globalsParameter = {'__builtins__': safe_builtins}
        globalsParameter['__builtins__']["__import__"] = self.fakeimport
        for el in context:
            globalsParameter[el] = context[el]
        f = StringIO()
        with redirect_stdout(f):
              exec(code, globalsParameter, globalsParameter)
        del globalsParameter['__builtins__']
        for el in globalsParameter:
            context[el] = globalsParameter[el]
        s = f.getvalue()
        return s

def readfile(fn):
    f = open(fn)
    p = f.read()
    f.close()
    return p

def try_solve_files(cl_args):
    for i, el in enumerate(cl_args):
        try:
            cl_args[i] = readfile(el)
        except:
            pass
    return cl_args

def merge_params(base,update):
        res = copy.deepcopy(base)
        for el in update:
            if el == "stop":
                stoparr = update[el]
                if isinstance(stoparr,str):
                    stoparr = [stoparr]

                if "stop" in res:
                    res["stop"].extend(stoparr)
                else:
                    res["stop"] = stoparr
            else:
                res[el] = update[el]
        return res

def get_input_simple(inprompt = "> "):
  prompt = input(inprompt)
  prompt_full = ""
  if len(prompt) > 0 and prompt[-1] == "\\":
    while len(prompt) > 0 and prompt[-1] == "\\":
      prompt = prompt[0:len(prompt)-1] +  "\n"
      prompt_full = prompt_full + prompt
      prompt = input(". ")
    prompt_full = prompt_full + prompt
  elif len(prompt) == 3 and prompt == "'''":
    prompt = input(". ")
    while len(prompt) != 3 or prompt != "'''":
      prompt_full = prompt_full + "\n" + prompt
      prompt = input(". ")
    prompt_full=prompt_full[1:]
  else:
    prompt_full = prompt_full + prompt
    
  return prompt_full

# tries to solve templates from the args stack. then it asks the user
def get_input(prompt_full="{}",args_stack=[]):
  inprompt = "> "
  if(prompt_full != "{}"):
      inprompt = "! "
  while True:
      prompt_full, need_more = solve_templates(prompt_full,args_stack)
      args_stack = []
      if not need_more:
          break
      prompt = get_input_simple(inprompt)
      inprompt = "! "
      prompt_full = prompt_full.replace("{}", prompt, 1)

  return prompt_full

def get_formatter(props):
  print(props["default_generation_settings"]["model"])
  model_path = props["default_generation_settings"]["model"]
  model_name = model_path.split("/")[-1]
  
  formatter = Formatter()
  formatter.load_model(model_name)
  return formatter
  

#una versione raw e una con tutte le regole
# se il primo è raw, allora skippa bos
# se un system segue un raw, allora non ha il preambolo
# se l'ultimo è un system, allora quel system non ha postambolo
# se l'ultimo è system o raw, allora non aggiungere finale

#import copy
#copy.deepcopy()

def apply_format_templates(formatter, prompt):
    return formatter.apply_format_templates( prompt)

def build_prompt(formatter,messages):
    return formatter.build_prompt(messages)



if __name__ == "__main__":
    import sys
    prompt = "TEST: {f:test/a.txt}"
    if(len(sys.argv) > 1):
      prompt = sys.argv[1]
      try:
        prompt=readfile(prompt)
      except:
        pass
    prompt,_ = solve_templates(prompt)
    print(prompt)
