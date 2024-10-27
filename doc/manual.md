# documentation

work in progress

## architecture

### **graph**

The core of the framework is executing a graph.
A graph is composed by nodes connected via directed arcs.
Each node processes information and sends the result along the outgoing arcs.

### **nodes**

Nodes are the processing elements in a graph.
A node receives data from incoming arcs, processes it with an executor and outputs the results.
Data is a array of elements. No constraint is imposed on the type of elements.

Nodes contain additional metadata that define how they behave inside the graph.
For example they can specify that they can be called only once, or specify that
the node should be called even if only some of the inputs are available.

### **executors**

The executor is a function or class that actually executes the computation.
Usually each node contains exactly one executor with the exception of the graph node.

## template
The input of a llm node is optionally templatized.

The base format is the following.
* **{p:bos}** to mark the begin of a templatized input
* **{p:user}** or **{p:assistant}** to mark the begin of a message. Notice that there is a newline after the tag
* **{p:end}** to mark the end of a message. There is no newline before the tag

```
{p:bos}

{p:user}
user query{p:end}

{p:assistant}
assistant response{p:end}
```

The template is **optional**. 

## variables

Nodes can set and read graph variables.
Variables can be used to fill templates in text based nodes.
To use a variable, add a placeholder `{v:variablename}`.

Special variables:
* **{p:execX}**: Input of the node in position X, starting from 1. Example: `{p:exec1}`
* **{v:_C[X]}**: The command line element in position X when the graph is launched via terminal. Example: `{v:_C[1]}`

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
