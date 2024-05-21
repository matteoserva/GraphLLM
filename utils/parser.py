
raw_tokens = ["<|im_start|>","<|START_OF_TURN_TOKEN|>","<BOS_TOKEN>","<|user|>","<|start_header_id|>"]
def check_special_tokens(m):
        special_tokens = ["{p:bos}","<|im_start|>","<|START_OF_TURN_TOKEN|>","<BOS_TOKEN>","<|user|>","<|start_header_id|>","{p:user}"]
        is_raw = False
        for el in special_tokens:
            if m.find(el) >= 0:
                is_raw = True
        return is_raw



def readfile(fn):
    f = open(fn)
    p = f.read()
    f.close()
    return p

def parse_raw(message):
    token = ""
    res = []
    for el in raw_tokens:
         if message.find(el) >= 0:
               raise Exception("found raw token")

    while True:
        m1 = -1
        for el in ["{p:system}\n","{p:user}\n","{p:assistant}\n"]:
            a = message.find(el)
            if a >= 0 and (m1 < 0 or a < m1):
                m1 = a
                token = el
        if m1 < 0:
            break;
        role = token[3:-2]
        message = message[m1+len(token):]
        m2 = message.split("{p:eom}",1)
        content = m2[0]
        res.append({"role":role,"content":content})
        if(len(m2) < 2):
            break;
        message = m2[1]
    if len(res) == 0:
         raise Exception("parser exception")
    return res

import re


def find_matching_parenthesis(test, start):
    initial_char = test[start]
    stack_pos = 1
    posB = test.find("}",start)
    return posB
  
def get_next_tag(prompt):
    pattern = re.compile("{[fsdrwv]:")
    b=pattern.search(prompt)
    if b is None:
      return None
    posA = b.start()
    if(posA < 0):
      return None;
    posB = find_matching_parenthesis(prompt,posA)
    
    if(posB < 0):
      return None;
    return posA,posB

def readstring_hierarchical(prompt,variables): 

  while True:
    tag = get_next_tag(prompt)
    if tag is None:
      break;
    posA,posB = tag

    foundString = prompt[posA:posB+1]
    tag = foundString[1]
    content = foundString[3:-1]
    if tag == "f":
        fnfull = content
        fnsplit = fnfull.split(",")
        fn = fnsplit[0]
        r = readfile(fn)
        r= readstring_hierarchical(r,variables)
        prompt = prompt.replace(foundString,r)
    elif tag == "s":
        prompt = prompt.replace(foundString, "",1)
        if prompt[0:posA].find("{}") >= 0:
          r = readfile(content)
          r= readstring_hierarchical(r,variables)
          prompt = prompt.replace("{}",r,1)
    elif tag == "w":
        fnfull = content
        r = scrape.scrape(fnfull)
        prompt = prompt.replace(foundString,r)
        print("newprompt: " + prompt + "-")
    elif tag == "v":
        fnfull = content
        r = variables[fnfull]
        prompt = prompt.replace(foundString,r)
    elif tag == "r": # fa una sostituzione dei {p:placeholder} con quello del {r:placeholder:nuovo}
        prompt = prompt.replace(foundString, "",1)
        content_array = content.split(":")
        to_replace = "{p:"+content_array[0]+"}"
        prompt = prompt.replace(to_replace, content_array[1])
    elif tag == "d":
        prompt = prompt.replace(foundString, "",1)
        if prompt[0:posA].find("{}") >= 0:
          r = content

          prompt = prompt.replace("{}",r,1)

  return prompt
 
# Cerca di risolvere tutti i template in questo formato:
#{f:summarize.txt,/tmp/pagina.md}  
# prima carica dal file, poi riempie tutti i {} con quelli che trova dopo
# 

def solve_templates(prompt,args_stack=[],variables={}):
    while True:
      prompt = readstring_hierarchical(prompt,variables)
      need_more = prompt.find("{}")>= 0 
      if not need_more or len(args_stack) == 0:
        break;
      prompt = prompt.replace("{}", args_stack[0], 1)
      args_stack = args_stack[1:]
      
    return prompt, need_more
