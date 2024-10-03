# documentation

work in progress

## architecture

**graph**
The core of the framework is executing a graph.
A graph is composed by nodes connected via directed arcs.
Each node processes information and sends the result along the outgoing arcs.

**executors**
Each node of the graph, the executor, executes a processing step.
The executor accepts an array of elements as input and produces an array of elements as its output.

Example executor: llm. It receives a prompt and produces the inference result
another executor: tool. It receives a tool name and parameters, it produces the result of a tool call

## template
The input of a llm node is templatized. The base format is the following.

"""
{p:bos}

{p:user}
user query{p:end}

{p:assistant}
assistant response{p:end}
"""

## graph
Each nodes can accept the following parameters:

- **type:** the type of node
- **init:** the initial template
- **deps:** dependencies that bypass the graph arcs
- **conf:** config parameters
- **exec:** executors used as input
 
Two special nodes are created implicitly: 
 
- **_C:** command line. It outputs the command line arguments during the call
- **_I:** input. Input data passed to the graph