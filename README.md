# GraphLLM

A graph based framework to process data through a LLM or multiple LLMs.

Several examples are available, including an agent capable of answering questions like

* `"give me a summary of the article on the home page of hacker news that is most likely related to language models."`

## Features:

Here are the features offered by GraphLLM:

* A graph based framework to process data using LLMs.
* A powerful agent capable of performing web searches and running python code
* A set of tools to scrape web pages and reformat data in a LLM friendly format
* A list of [examples](https://github.com/matteoserva/GraphLLM/tree/main/examples) to start from
* It's a very low level framework. You get full control over the raw prompt and you see the raw output of the models.
  The inner working of the library is not hidden by any abstraction
* The GUI is a work in progress but it's there

![image](https://github.com/user-attachments/assets/1e265b4c-f4c9-48f1-8a88-40d8bcf01e0a)
    
## The GUI

GraphLLM provides a GUI inspired by ComfyUI. The frontend has a similar look but the backend is completely different, so the nodes are not compatible between the project.
The reason for this is that I wanted to provide more advanced features and support complex graphs.

Some of the features of GraphLLM's GUI:
- **loops**: You can have any kind of loop in the graph or even run a graph infinitely
- **conditionals**: The graph topology can be partially altered by the value going into nodes. This is useful for building state machines
- **parallel execution** of nodes: More nodes can be executing in parallel, useful for making multiple LLM calls at the same time
- **streaming of results**: Output of the LLM nodes can be seen in real time while it's produced. Watch nodes can be connected while the graph is running.
- **Hierarchical graphs**: Graphs can contain other graphs without limits.
- **extra features**: The graph can call external tools, for example the web scraper, the youtube downloader or the pdf reader

Here is an example of graph to generate python code and use it to solve a problem:

https://github.com/user-attachments/assets/486176d6-5bd7-4953-80fb-dbf7edb9af48

**Another example:**
<details>

<summary>Expand here to see another sample graph</summary>

### This is a simple graph to iteratively edit a file.

https://github.com/user-attachments/assets/80d5331a-efab-429a-bf51-991feaa64e1d

</details>

## Limitations:

* Tested mainly with llama70b and qwen 32b, using the llama.cpp server as backend
* Under heavy development, expect breaking changes

## setup

### quick setup

Run these commands in a shell to download and start GraphLLM

- `pip3 install selenium readabilipy html2text pdfminer.six justpy`
- `git clone https://github.com/matteoserva/GraphLLM.git`
- `cd GraphLLM`

In another terminal, launch the llama.cpp server with Qwen2.5 32b.:

- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 CUDA_VISIBLE_DEVICES=0,1 ./llama-server -ngl 99 -t 6 -c 32768 --host 0.0.0.0  -m Qwen2.5-32B-Instruct-Q5_K_M.gguf --override-kv tokenizer.ggml.add_bos_token=bool:false -sp -fa -ctk q8_0 -ctv q8_0`

### detailed setup

<details>

<summary>Expand here to see a more detailed explanation of the setup steps</summary>

### dependencies
**Required**

TBD. When a missing dependency occurs, run `pip3 install {dependency}`

**optional**

There are optional dependencies for the extra features:
- pdfminer.six for converting PDF files
- justpy for the web server
- selenium for the web scraping tool
- firefox and its Webdriver, for the web scraping tool

Install the python dependencies with

`pip3 install selenium readabilipy html2text pdfminer.six justpy`


### hello world
The example runs a python node that prints `hello world` multiple times.

run `python3 exec.py examples/graph_python_hello_world.txt`

### setup the connection with the llama.cpp server
Steps to configure a connection with [llama.cpp](https://github.com/ggerganov/llama.cpp)

**llama.cpp server**

- Launch the server with

  `./llama-server -ngl 99 -t 4 -c 32768 --host 0.0.0.0 -m {your_model} --override-kv tokenizer.ggml.add_bos_token=bool:false -sp -fa`
  
  Relevant arguments:
  - `-host 0.0.0.0` if you want to run the server on another machine
  - `--override-kv tokenizer.ggml.add_bos_token=bool:false` to avoid auto inserting a bos token. GraphLLM already adds it
  - `-sp` To receive the eom token, this enables llama3.1 tool calling
  - `-m {your_model}` selects the model to use. This project works best with llama 3.1 or qwen2.5

**client configuration**

- modify `client_config.yml`

  - replace `client_name: dummy` with `client_name: llama_cpp`
  - if needed, change the host and port for the llama_cpp section

### setup the extra tools

**web scraper**
- install firefox and selenium
- open firefox
- open about:profiles
- create a profile named "profile.bot"
- relaunch inside that profile
- install ublock origin and verify that it's working.
- close firefox
- If needed, download the appropriate [geckodriver](https://github.com/mozilla/geckodriver/releases)
- test the tool with `python3 extras/scraper/scrape.py`

**pdf scraper**
- install pdfminer.six
- test it by running `python3 extras/parse_pdf.py {your pdf}`

**youtube scraper**
- test it by running `python3 extras/youtube_subs.py`

</details>

## running the example

**launching the server**

You can launch the server by running this command in a terminal from inside the GraphLLM folder:
- `python3 server.py`

Then you can open the browser at http://localhost:8008/

**directly running a graph**    

This will launch the example summarization prompt:
  
- `python3 exec.py examples/graph_summarize.txt test/wikipedia_summary.txt`

**all the examples**

There are more examples in the [examples folder](https://github.com/matteoserva/GraphLLM/tree/main/examples)
You can also open more example from the web gui

## Backend support

GraphLLM supports some inference engines and many models. The suggested combination is llama.cpp with Qwen2.5.

**inference engines and API**

The llama.cpp server is fully supported. Other engines are available with limited functionality.
GraphLLM makes extensive use of advanced features like grammars, assistant response prefilling and using raw prompts.
Some engines and API providers support only a subset of these features.

Available engines:
- llama.cpp server: complete support
- groq API: Grammars and raw prompts not available
- OpenAI API: WIP
- HF transformers: partial support

**models**

All the popular models are available.

# Thanks

* [litegraph](https://github.com/jagenjo/litegraph.js)
* [llama.cpp](https://github.com/ggerganov/llama.cpp)
