# GraphLLM

A graph based framework to process data through a LLM or multiple LLMs.

Several examples are available, including an agent capable of answering questions like

* `"give me a summary of the article on the home page of hacker news that is most likely related to language models."`

## Features:

Here are the features offered by GraphLLM:

* A graph based framework to process data using LLMs.
* A powerful agent capable of performing web searches and running python code
* A set of tools:
    * **web scraper** to scrape web pages and reformat data in a LLM friendly format.
    * **PDF parser** To extract text from PDF files.
    * **youtube subs downloader** to download subtitles from a youtube video.
    * **Python sandbox** for safely executing code generated by a LLM.
    * **TTS engine** using piper.
* **GUI** for building and debugging graphs with a nice interface

![Screenshot_20241025_200056](https://github.com/user-attachments/assets/b2e38b92-e247-4fb8-b593-948909224b5b)

A list of [examples](https://github.com/matteoserva/GraphLLM/tree/main/examples) is available as a starting point.

This is a very low level framework. You get full control over the raw prompt and you see the raw output of the models.
The inner working of the library is not hidden by any abstraction. The disadvantage is a steeper learning curve.
    
## The GUI

GraphLLM provides a GUI inspired by ComfyUI. The frontend has a similar look but the backend is completely different, so the nodes are not compatible between the project.
The reason for this is that I wanted to provide more advanced features and support complex graphs.

Some of the features of GraphLLM's GUI:
- **loops**: You can have any kind of loop in the graph or even run a graph infinitely
- **conditionals**: The graph topology can be partially altered by the value going into nodes. This is useful for building state machines
- **parallel execution** of nodes: More nodes can be executing in parallel, useful for making multiple LLM calls at the same time
- **streaming of results**: Output of the LLM nodes can be seen in real time while it's produced. Watch nodes can be connected while the graph is running.
- **Hierarchical graphs**: Graphs can contain other graphs without limits.
- **external tools**: The graph can call external tools, for example the web scraper, the youtube downloader or the pdf reader
- **dynamic scheduling** of nodes when they are runnable

Here is an example of graph to generate python code and use it to solve a problem:

https://github.com/user-attachments/assets/486176d6-5bd7-4953-80fb-dbf7edb9af48

**More examples:**
<details>

<summary>Expand here to see more examples</summary>

### Iteratively edit a file.

This video showcases the File Node and how to make multiple calls to a LLM.

https://github.com/user-attachments/assets/80d5331a-efab-429a-bf51-991feaa64e1d

### Download a file, then call another graph to summarize it

This screenshot show a Hierarchical graph. The file is downloaded, then summarized using another graph

![image](https://github.com/user-attachments/assets/d56cf883-484c-4a93-8d07-74ab33c2f6f9)

</details>

## Limitations:

* Tested mainly with llama70b and qwen 32b, using the llama.cpp server as backend
* Under heavy development, expect breaking changes

## setup

### quick setup

Run these commands in a shell to download and start GraphLLM

- `pip3 install selenium readabilipy html2text pdfminer.six websockets jinja2`
- (optional) `pip3 install piper-tts`
- `git clone https://github.com/matteoserva/GraphLLM.git`
- `cd GraphLLM`
- `python3 server.py`

In another terminal, launch the llama.cpp server with Qwen2.5 32b.:

- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 ./llama-server -ngl 99 -t 6 -c 32768 --host 0.0.0.0 -sp -fa -ctk q8_0 -ctv q8_0 -m Qwen2.5-32B-Instruct-Q5_K_M.gguf`

Now you can launch the browser and interact with GraphLLM:

- Open [http://localhost:8008/](http://localhost:8008/) in a web browser

Some tools require further configuration steps, namely the web scraper.
Open the detailed setup page below to view the configuration steps.

### detailed setup

<details>

<summary>Expand here to see a more detailed explanation of the setup steps</summary>

### dependencies
**Required**

TBD. When a missing dependency occurs, run `pip3 install {dependency}`

**optional**

There are optional dependencies for the extra features:
- pdfminer.six for converting PDF files
- selenium for the web scraping tool
- firefox and its Webdriver, for the web scraping tool
- openai and groq API
  
Install the python dependencies with

`pip3 install selenium readabilipy html2text pdfminer.six openai groq websockets piper-tts`

### setup the connection with the llama.cpp server
Steps to configure a connection with [llama.cpp](https://github.com/ggerganov/llama.cpp)

**llama.cpp server**

- Launch the server with

  `./llama-server -ngl 99 -t 4 -c 32768 --host 0.0.0.0 -m {your_model} -sp -fa`
  
  Relevant arguments:
  - `-host 0.0.0.0` if you want to run the server on another machine
  - `-sp` To receive the eom token, this enables llama3.1 tool calling
  - `-m {your_model}` selects the model to use. This project works best with llama 3.1 or qwen2.5

**client configuration**

- modify `client_config.yml`

  - You can replace the default client by changing the `client_name` parameter in the config file
  - If needed, setup groq or openai api config
  - You can use a list as client_name. In that case if one client fails, the next one will be used.
    For example you can use this to setup llama.cpp as primary client and a remote API as fallback.

### setup the extra tools

**web scraper**
- install firefox and selenium
- open firefox
- open about:profiles
- create a profile named "profile.bot"
- relaunch inside that profile
- install ublock origin and verify that it's working.
- import the ublock filter list I uploaded [here](https://github.com/matteoserva/GraphLLM/blob/main/doc/ublock-backup.txt)
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
- **llama.cpp** server: complete support
- **llama_swap**: full support
- **groq** API: Grammars and raw prompts not available
- **openrouter** API: Grammars and raw prompts not available
- **OpenAI** and compatible API: Grammars and raw prompts not available
- **HF transformers**: partial support

**models**

All the popular models are available.

# Thanks

* [litegraph](https://github.com/jagenjo/litegraph.js)
* [llama.cpp](https://github.com/ggerganov/llama.cpp)
* [showdown](https://github.com/showdownjs/showdown)
