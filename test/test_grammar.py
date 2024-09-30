import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from modules.grammar import load_grammar 

a = load_grammar("grammars/json_response.txt")
print(a)
a = load_grammar("grammars/react_text.txt")
print(a)
