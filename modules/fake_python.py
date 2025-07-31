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

class _fake_method:
    def __init__(self,method_name):
        self.method_name = method_name

    def open(self,fname, mode,*args, **kwargs):
        #print(args,kwargs)
        if fname.startswith(tempfile.gettempdir() + "/"):
            return open(fname,mode,*args, **kwargs)
        if fname.startswith("test/") or fname.startswith("tests/"):
            return open(fname,mode,*args, **kwargs)
        raise Exception("the open() function must be used on files in the " + tempfile.gettempdir() + " directory")
    
    def _call_method(self,method_name,*args, **kwargs):
        f = getattr(self,method_name)
        return f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._call_method(self.method_name,*args, **kwargs)

class _fake_module:
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
                return _fake_module(newName,self.subimports[newName],self.subimports)
        return partial( self._wrapper_method, self.module_name, key)

    def remove (self, name):
         print ("file removed successfully: ", name) # questo vince sulla risoluzione generica

    def _wrapper_method(self,modname, funcname, *args, **kwargs):
        if funcname in self.attrs:
            m = getattr(self.mod,funcname)
            return m(*args, **kwargs)

def _my_exec(code, globals, locals):
    a = ast.parse(code)
    last_expression = None
    if a.body:
        if isinstance(a_last := a.body[-1], ast.Expr):
            last_expression = ast.unparse(a.body.pop())
    exec(ast.unparse(a), globals, locals)
    if last_expression:
        return eval(last_expression, globals, locals)
    if a.body and isinstance(a.body[-1], ast.Assign):
        try:
            target_name = a.body[-1].targets[0].id
            val = locals[target_name]
            return val
        except:
            pass


class FakePython:
    def __init__(self):
        self.safe_builtins = ["int", "float","sum", "max", "min", "abs", "range", "str", "print","dir","len","next","enumerate"]
        self.safe_imports = ["re","sympy","numpy","datetime","bs4","requests","webbrowser","json","numpy.polynomial.polynomial","math","scipy.optimize"]
        self.fake_imports = {"os":["listdir","path"]}
        self.fake_subimports = {"os.path":["getsize","isfile"]}
        self.fake_builtins = {"open":_fake_method}
        pass

    def fakeimport(self, name, *args,**kwargs):
        #print("fakeimport", name, args,kwargs)
        if name in self.safe_imports:
            #res = __import__(name,fromlist=[None])
            res = importlib.import_module(name)
            return res
        if name in self.fake_imports:
            return _fake_module(name,self.fake_imports[name],self.fake_subimports)

    def makeGlobals(self):
        current_builtins = {}
        for el in self.safe_builtins:
            current_builtins[el] = getattr(builtins, el)
        for el in self.fake_builtins:
            current_builtins[el] = _fake_method(el)
        globalsParameter = {'__builtins__': current_builtins}
        globalsParameter['__builtins__']["__import__"] = self.fakeimport
        globalsParameter['__builtins__']["__name__"] = "__main__"
        return globalsParameter



class PythonInterpreter:
    def __init__(self):
        self.fake_python = FakePython()

    def execute(self,code, context):
        globalsParameter = self.fake_python.makeGlobals()
        for el in context:
            globalsParameter[el] = context[el]
        f = StringIO()
        with redirect_stdout(f):
            #alt_s = my_exec(code, globalsParameter, globalsParameter)
            try:
                alt_s = _my_exec(code, globalsParameter, globalsParameter)
            except Exception as e:
                raise
            #    traceback.print_exc()
            #    traceback.print_exception(*sys.exc_info())
            #    print(str(type(e).__name__ ) + ": " + str(e))
        del globalsParameter['__builtins__']
        for el in globalsParameter:
            context[el] = globalsParameter[el]
        s = f.getvalue()
        if not s and alt_s:
            s = str(alt_s)
        return s


import code
import io
class PythonConsole:
    def __init__(self):
        self.fake_python = FakePython()
        self._console = None
        self._stdout_capture = io.StringIO()
        self._stderr_capture = io.StringIO()
    
    def __pprint(self, *args,**kwargs):
        kwargs["file"] = self._stdout_capture
        print(*args,**kwargs)
    
    
    def reset(self, extraContext = {}):
        globalsParameter = self.fake_python.makeGlobals()
        globalsParameter['__builtins__']["print"] = self.__pprint
        for el in extraContext:
            if el not in globalsParameter:
                globalsParameter[el] = extraContext[el]
        self._console = code.InteractiveConsole(locals=globalsParameter)
        self._console.write = self._stderr_capture.write
        self._last_retval = False
    
    def _pushline(self, code):
        if code.startswith(">>> ") or code.startswith("... "):
            code = code[4:]
        elif code.startswith(">>>") or code.startswith("..."):
            code = code[3:]
        retval = self._console.push(code)
        
        output = self._stdout_capture.getvalue()
        error = self._stderr_capture.getvalue()
        
        # Reset the IO buffers for the next call
        self._stdout_capture.seek(0)
        self._stdout_capture.truncate(0)
        self._stderr_capture.seek(0)
        self._stderr_capture.truncate(0)
        
        prompt = "... " if self._last_retval else ">>> "
        self._last_retval = retval
            
        
        combined_output = prompt + code + "\n" + error + output
        
        return combined_output
        
    def push(self, code):
        results = [self._pushline(el) for el in code.split("\n")]
        textout = "".join(results)
        print(textout,end="")
        return textout
            
        

code1 = """
print('ciao')
for i in range(4):
    pricnt(i)

print('ciao',end="")
"""

console = PythonConsole()
console.reset()
console.push(code1)
console.push("a = 3")
console.push("print(a)")
