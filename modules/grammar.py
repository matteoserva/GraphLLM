import json

def load_grammar_text(a):
    res = {}
    try:
        res["schema"] = json.loads(a)
        res["format"] = "json_schema"
    except:
        res["schema"] = a
        res["format"] = "grammar"
    return res

def load_grammar(fn):
    f = open(fn,"r")
    a = f.read()
    f.close()
    return load_grammar_text(a)