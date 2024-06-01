import json

def load_grammar(fn):
    f = open(fn,"r")
    a = f.read()
    f.close()
    res = {}
    try:
        res["schema"] = json.loads(a)
        res["format"] = "json_schema"
    except:
        res["schema"] = a
        res["format"] = "grammar"
    return res
