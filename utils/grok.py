from groq import Groq
client = Groq(api_key="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")

messages=[ { "role": "user", "content": "Hello, tell me your name" }]

params={ "temperature":1, "max_tokens":1024, "top_p":1, "stream":True, "stop":None}

completion = client.chat.completions.create( model="llama3-8b-8192", messages=messages,**params) 

for chunk in completion:
   print(chunk.choices[0].delta.content or "", end="")
