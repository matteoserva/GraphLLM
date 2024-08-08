from io import StringIO
from contextlib import redirect_stdout
import builtins
from functools import partial
import importlib
import types

class fake_method:
    def __init__(self,method_name):
        self.method_name = method_name

    def open(self,fname, mode,*args, **kwargs):
        #print(args,kwargs)
        if fname.startswith("/tmp/"):
            return open(fname,mode,*args, **kwargs)
    
    def _call_method(self,method_name,*args, **kwargs):
        f = getattr(self,method_name)
        return f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._call_method(self.method_name,*args, **kwargs)

class fake_module:
    def __init__(self,module_name,module_attrs):
        self.module_name = module_name
        self.mod = importlib.import_module(module_name)
        self.attrs = module_attrs
    def __getattr__(self, key):
        m = getattr(self.mod,key)
        if isinstance(m,types.ModuleType):
            newName = self.module_name + "." + key
            return fake_module(newName,["getsize"])
        return partial( self.wrapper_method, self.module_name, key)

    def wrapper_method(self,modname, funcname, *args, **kwargs):
        if funcname in self.attrs:
            m = getattr(self.mod,funcname)
            return m(*args, **kwargs)

class PythonInterpreter:
    def __init__(self):
        self.safe_builtins = ["sum", "range", "int", "print","dir"]
        self.safe_imports = ["sympy","numpy","datetime","bs4","requests"]
        self.fake_imports = {"os":["listdir"]}
        self.fake_builtins = {"open":fake_method}
        pass

    def fakeimport(self, name, *args,**kwargs):
        #print("fakeimport", name, args,kwargs)
        if name in self.safe_imports:
            return __import__(name)
        if name in self.fake_imports:
            return fake_module(name,self.fake_imports[name])

    def execute(self,code, context):
        current_builtins = {}
        for el in self.safe_builtins:
            current_builtins[el] = getattr(builtins, el)
        for el in self.fake_builtins:
            current_builtins[el] = fake_method(el)
        globalsParameter = {'__builtins__': current_builtins}
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