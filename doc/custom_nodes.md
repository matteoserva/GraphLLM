# Custom Node Development

Custom nodes can be defined by three main components:
- **GUI**: This is frontend node for interaction with the user
- **Parser**: Parses the GUI state to generate the backend node configuration
- **Executor**: Backend node that executes the computation.

Frontend nodes and Backend nodes are defined independently. The parser is responsible for mapping frontend and backend.

## 1. GUI Component (BaseGuiNode)
Defines the node's user interface.
Inherits `BaseGuiNode` and must define a class variable `node_title` that is shown in the GUI.
Elements are added through the `builder` helper.

```python
from modules.executors.common import BaseGuiNode

class SimpleGui(BaseGuiNode):
    node_type="simple_gui"

    def buildNode(self):
        builder = self._initBuilder()

        builder._addOutput("out", "string");
        builder._addCustomWidget("textarea", "widget name", {"property": "textarea_identifier"})

        return builder
```

## 2. Parser (BaseGuiParser)
Responsible for configuration parsing and validation.

Maps the gui node to the backend node.
More complex nodes can reuse the same backend node for multiple GUI nodes.
The opposite is also possible.

Inherits `BaseGuiParser`.
Must define `node_types`: a list of GUI nodes that will use this parser.

It returns the configuration for the backend node
```python
from modules.executors.common import BaseGuiParser

class SimpleParser():
    node_types = ["simple_gui"]
```

## 3. Executor (GraphExecutor)
Contains the core execution logic.
Must define `node_type` to identify the node.

The function `__call__` is executed every time the inputs are available.

```python
from modules.executors.common import GenericExecutor

class SimpleNode(GenericExecutor):
    node_type = "simple_gui"

    def __call__(self, inputs, *args):
        textarea_value = self.properties["textarea_identifier"]
        output0 = textarea_value
        outputs = [output0]
        return outputs
```

