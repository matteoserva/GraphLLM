A graph based framework to process data through a LLM or multiple LLMs.

# setup

## quick setup
- run `git clone https://github.com/matteoserva/GraphLLM.git`
- cd GraphLLM

## python dependencies
TBD. When a missing dependency occurs, run `pip3 install {dependency}`

## hello world
The example runs a python node that prints `hello world` multiple times.

run `python3 exec.py examples/graph_python_hello_world.txt`

## setup a client
Steps to configure a connection with [llama.cpp](https://github.com/ggerganov/llama.cpp)
- Launch the server with `./llama-server -ngl 99 -t 4 -c 32768 --host 0.0.0.0 -m {your_model} --override-kv tokenizer.ggml.add_bos_token=bool:false -sp -fa`
  
  Relevant arguments:
  - `-host 0.0.0.0` if you want to run the server on another machine
  - `--override-kv tokenizer.ggml.add_bos_token=bool:false` to avoid auto inserting a bos token. GraphLLM already adds it
  - `-sp` To receive the eom token, this enables llama3.1 tool calling
  
- launch the example react prompt:
  `python3 exec.py examples/graph_python_hello_world.txt`

  This launches a react agent that has to perform mathematical operations using the provided tools.
  
  Gotchas:
  - There is no direct tool to execute the operation. The model is forced to combine the available tools to complete the request
  - The model is not allowed to see the partial results. The errors should provide a hint about what to do next
