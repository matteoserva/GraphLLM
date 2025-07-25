# backend node development

### node lifetime

- setup
- execution

#### setup
- **constructor**: Creates the node
- **initialize()**: The node can access the graph 
- **set_parameters()**: Configuration of the node
- **setup_complete()**: After all nodes are configured

#### execution
- **graph_started()**: Called once when the graph is started
- **\_\_call\_\_()**: Called every time inputs are available
- **graph_stopped()**: Called once when the graph is stopped
