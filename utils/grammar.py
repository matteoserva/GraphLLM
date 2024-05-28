import json

def load_grammar(fn):
    f = open(fn,"r")
    a = f.read()
    f.close()
    res = {}
    try:
        res["grammar"] = json.loads(a)
        res["format"] = "json"
    except:
        res["grammar"] = a
        res["format"] = "formal"
    return res
