

The node parser reads a gui node and generates the backend node configuration.
It can return a single node or a list of nodes.
Work in progress. Right now use the default implementation:


### default implementation
```
from modules.executors.common import BaseGuiParser

class SimpleParser(BaseGuiParser):
    node_types = ["simple_gui"]
```

### simple node

Specify a new type for the backend node
```
class Test2Parser(BaseGuiParser):
    node_types = ["test_subparser"]

    def parse_node(self,new_config):
        new_config["type"] = "copy"
        return new_config
```

### complex node
- The inputs are passed in new_node["exec"]
- The last node must be a `nop` node
- Each internal node should have an id that can be referenced

```
class Test2Parser(BaseGuiParser):
    node_types = ["test_subparser"]

    def parse_node(self,old_config):
        new_config = self._make_default_config(old_config)

        inputs = new_config["exec"]
        conf1 = { "id": "geronimo", "exec": inputs, "type": "delay", "conf": { "delay":4.0}}
        conf2 = {"type": "delay", "conf": { "delay":4.0}, "exec":["geronimo[0]"]}
        new_config = [conf1,conf2]
        return new_config
```