
from ..formatter import Formatter
from ..formatter import solve_templates
import copy
from ..fake_python import PythonInterpreter


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
