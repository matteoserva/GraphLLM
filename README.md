# GraphLLM

A graph based framework to process data through a LLM or multiple LLMs.

## setup

### quick setup
- run `git clone https://github.com/matteoserva/GraphLLM.git`
- `cd GraphLLM`

### dependencies
**Required**

TBD. When a missing dependency occurs, run `pip3 install {dependency}`

**optional**

There are optional dependencies for the extra features:
- pdfminer.six for converting PDF files
- justpy for the web server
- selenium for the web scraping tool
- firefox and its Webdriver, for the web scraping tool

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

**running the example**
    
- launch the example summarization prompt:
  
  `python3 exec.py examples/graph_summarize.txt test/wikipedia_summary.txt`

  This launches a summarization example.

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

## launch the examples

There are more examples in the [examples folder](https://github.com/matteoserva/GraphLLM/tree/main/examples)
Have fun.
