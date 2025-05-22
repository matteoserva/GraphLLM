import copy

def readfile(fn):
    f = open(fn)
    p = f.read()
    f.close()
    return p

def merge_params(base, update):
    res = copy.deepcopy(base)
    for el in update:
        if el == "stop":
            stoparr = update[el]
            if isinstance(stoparr, str):
                stoparr = [stoparr]

            if "stop" in res:
                res["stop"].extend(stoparr)
            else:
                res["stop"] = stoparr
        else:
            res[el] = update[el]
    return res