
### hello world

runs a python node that prints hello world multiple times

`python3 exec.py examples/graph_python_hello_world.txt`

---

### summarize a file

Summarize a wikipedia article

`python3 exec.py graphs/summarize_file.txt test/wikipedia_summary.txt`

### Query file

`python3 exec.py graphs/query_file.txt test/wikipedia_summary.txt "what is the topic of the article?`

### summarize youtube video, multistep

`python3 exec.py graphs/youtube_summarize.txt test/yt_recap_2018.txt`

### majority voting, multi node

`python3 exec.py graphs/majority.txt test/problem_cubesum.txt`

### python, generate and execute

`python3 exec.py graphs/python_gen_exec.txt test/problem_cubesum.txt`

---

### ReAct, text based pattern

`python3 exec.py examples/react_text.txt test/react_cubesum2.txt`

The model has to perform mathematical operations using the provided tools.
  
  Gotchas:
  - There is no direct tool to execute the operation. The model is forced to combine the available tools to complete the request
  - The model is not allowed to see the partial results. The errors should provide a hint about what to do next

### ReAct, python pattern

`python3 exec.py examples/react_python.txt test/template_react_python.txt`

### ReAct, xml+python pattern

`python3 exec.py examples/react_xml_mixed.txt`

### ReAct, pure xml pattern

`python3 exec.py examples/react_xml_pure.txt "What is the cube of the sum of these three numbers: 16,5,11?"`

---

## Full agent

This example is a full agent using the ReAct + reflexion pattern.
The agent has access to all implemented tools.
It is allowed to open webpages and execute python code.
Only files in /tmp are accessible.

> [!NOTE]
> This has been tested with Qwen2.5 32b and the llama_cpp backend. Llama 70b should work. Smaller models might not be smart enough to perform correctly

**find, download and summarize an article**

`python3 exec.py graphs/agent_reflexion.txt "give me a summary of the article on the home page of hacker news that is most likely related to language models."`

**ask the current weather**

`python3 exec.py graphs/agent_reflexion.txt "what is today's weather in rome?"`

**finding a recipe**

`python3 exec.py graphs/agent_reflexion.txt "what is the recipe of pasta alla carbonara?"`
