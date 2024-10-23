from io import StringIO
from contextlib import redirect_stdout
import builtins
from functools import partial
import importlib
import types
import traceback 
import sys
import ast
import tempfile

class fake_method:
    def __init__(self,method_name):
        self.method_name = method_name

    def open(self,fname, mode,*args, **kwargs):
        #print(args,kwargs)
        if fname.startswith(tempfile.gettempdir() + "/"):
            return open(fname,mode,*args, **kwargs)
        if fname.startswith("test/"):
            return open(fname,mode,*args, **kwargs)
        raise Exception("the open() function must be used on files in the " + tempfile.gettempdir() + " directory")
    
    def _call_method(self,method_name,*args, **kwargs):
        f = getattr(self,method_name)
        return f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._call_method(self.method_name,*args, **kwargs)

class fake_module:
    def __init__(self,module_name,module_attrs, subimports):
        self.module_name = module_name
        self.mod = importlib.import_module(module_name)
        self.attrs = module_attrs
        self.subimports = subimports
    def __getattr__(self, key):
        m = getattr(self.mod,key)
        if isinstance(m,types.ModuleType):
            newName = self.module_name + "." + key
            if newName in self.subimports:
                return fake_module(newName,self.subimports[newName],self.subimports)
        return partial( self._wrapper_method, self.module_name, key)

    def remove (self, name):
         print ("file removed successfully: ", name) # questo vince sulla risoluzione generica

    def _wrapper_method(self,modname, funcname, *args, **kwargs):
        if funcname in self.attrs:
            m = getattr(self.mod,funcname)
            return m(*args, **kwargs)

def my_exec(code, globals, locals):
    a = ast.parse(code)
    last_expression = None
    if a.body:
        if isinstance(a_last := a.body[-1], ast.Expr):
            last_expression = ast.unparse(a.body.pop())
    exec(ast.unparse(a), globals, locals)
    if last_expression:
        return eval(last_expression, globals, locals)

class PythonInterpreter:
    def __init__(self):
        self.safe_builtins = ["sum", "max", "min", "range", "int", "str", "print","dir","len","next","enumerate"]
        self.safe_imports = ["sympy","numpy","datetime","bs4","requests","webbrowser","json","numpy.polynomial.polynomial","math","scipy.optimize"]
        self.fake_imports = {"os":["listdir","path"]}
        self.fake_subimports = {"os.path":["getsize","isfile"]}
        self.fake_builtins = {"open":fake_method}
        pass

    def fakeimport(self, name, *args,**kwargs):
        #print("fakeimport", name, args,kwargs)
        if name in self.safe_imports:
            #res = __import__(name,fromlist=[None])
            res = importlib.import_module(name)
            return res
        if name in self.fake_imports:
            return fake_module(name,self.fake_imports[name],self.fake_subimports)

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
            try:
                alt_s = my_exec(code, globalsParameter, globalsParameter)
            except Exception as e:
                #traceback.print_exc() 
                #traceback.print_exception(*sys.exc_info()) 
                print(str(type(e).__name__ ) + ": " + str(e))
        del globalsParameter['__builtins__']
        for el in globalsParameter:
            context[el] = globalsParameter[el]
        s = f.getvalue()
        if not s and alt_s:
            s = str(alt_s)
        return s
