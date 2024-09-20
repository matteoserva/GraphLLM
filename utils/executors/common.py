
def send_chat(builder,client,client_parameters=None,print_response=True):
    r = client.send_prompt(builder,params=client_parameters)
    ret = ""
    for line in r:
        if print_response:
             print(line, end="", flush=True)
        ret = ret + line
    if print_response and print_response != "partial":
        print("")
    return ret

def solve_placeholders(base, confArgs, confVariables={}):
        for i in range(len(confArgs)):
            name = "{p:exec" + str(i + 1) + "}"
            val = confArgs[i]
            base = base.replace(name, val)
        for el in confVariables:
            name = "{p:" + el + "}"
            val = confVariables[el]
            base = base.replace(name, val)
        return base