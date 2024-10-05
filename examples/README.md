# Examples using GraphLLM

## basic examples

### hello world

runs a python node that prints hello world multiple times

`python3 exec.py examples/graph_python_hello_world.txt`

---

## intermediate examples

> [!NOTE]
> For these examples you need a backend. You should edit client_config.yml to use llama.cpp

### using a templated prompt

uses a template:

`python3 exec.py graphs/run_template.txt examples/template_full.txt`

### summarize a file

Summarize a wikipedia article

`python3 exec.py graphs/summarize_file.txt test/wikipedia_summary.txt`

### Query file

`python3 exec.py graphs/query_file.txt test/wikipedia_summary.txt "what is the topic of the article?"`

### summarize youtube video, multistep

`python3 exec.py graphs/youtube_summarize.txt test/yt_recap_2018.txt`

### majority voting, multi node

`python3 exec.py graphs/majority.txt test/problem_cubesum.txt`

### python, generate and execute

`python3 exec.py graphs/python_gen_exec.txt test/problem_cubesum.txt`

### rap battle

`python3 exec.py examples/rap_battle.txt python C`

### named entity recognition

Two step graph that extracts the entities and then queries the model again for the relations

`python3 exec.py graphs/ner.txt test/ner_podcast.txt`

### llama 3.1 native tool call.

For this example you have to make sure that the llama.cpp server is launched with `-sp`

`python3 exec.py graphs/llama3.1_native_python.txt "tell me the current date and time"`

**chat with a pdf**

This is a stateless chat about a pdf file.
The model doesn't keep the history of previous questions.

`python3 exec.py graphs/chat_with_pdf.txt test/sample.pdf`

**rewrite a question and solve it using python code** 

TThis is an example of a hierarchical graph.

Here is the base graph that rewrites a question to make it more understandable:

`python3 exec.py examples/rewrite_question.txt test/problem_cubesum.txt`

But the base graph can also be a node from a higher level graph.
This uses the rewritten quesition to generate python code and execute it to solve the original problem.

`python3 exec.py examples/rewrite_python.txt test/problem_cubesum.txt`

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

## Advanced examples

For these examples you need the extra tools to be properly configured.

### Web tools and scraper

**scrape a web page**

This converts a webpage to markdown and saves the result to /tmp/pagina.md

`python3 extras/scraper/scrape.py https://en.wikipedia.org/wiki/Language_model`

**download youtube subtitles**

Downloads subtitles from a youtube url and saves them to /tmp/yt_transcript.txt:

`python3 extras/youtube_subs.py https://www.youtube.com/watch?v=YbJOTdZBX1g`

**extract data from a pdf**

`python3 extras/parse_pdf.py test/sample.pdf`

### Full agent

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

**summarize a wikipedia page**

`python3 exec.py graphs/agent_reflexion.txt "summarize https://en.wikipedia.org/wiki/Language_model"`

**solve a cubic equation**

`python3 exec.py graphs/agent_reflexion.txt "solve this: x^3 - 4x^2 + 6x - 24 = 0"`
