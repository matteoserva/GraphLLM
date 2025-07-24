# Custom Node Development

Custom nodes can be defined by three main components:
- **GUI**: This is frontend node for interaction with the user
- **Parser**: Parses the GUI state to generate the backend node configuration
- **Executor**: Backend node that computes the output when a new input is available.

Frontend nodes and Backend nodes are defined independently. The parser is responsible for mapping frontend and backend.

## 1. GUI Component (BaseGuiNode)
Defines the node's user interface.
Inherits `BaseGuiNode` and must define a class variable `node_title` that is shown in the GUI.
Elements are added through the `builder` helper.

```python
from modules.executors.common import BaseGuiNode

class RepeatGui(BaseGuiNode):
    node_title="Simple Gui"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._getBuilder()

        builder._reset()
        builder._addInput("in","string");
        builder._addOutput("out", "string");

        builder._addCustomWidget("textarea", "widget name", {"property": "textarea_identifier"})

        builder._setPath("simple_gui")
```

## 2. Parser (BaseGuiParser)
Responsible for configuration parsing and validation.
Inherits `BaseGuiParser`.
Must define `node_types`: a list of GUI nodes that will use this parser.
The name of the gui node has been set with `builder._setPath()`.
It returns the configuration for the backend node
```python
from modules.executors.common import BaseGuiParser

class SimpleParser(BaseGuiParser):
    node_types = ["simple_gui"]

    def parse_node(self, old_config):
        new_config = {}
        new_config["type"] = "simple_node"

        # read the widget values
        properties = old_config.get("properties", {})
        textarea_value = properties.get("textarea_identifier", "")
        new_config["init"] = [textarea_value]

        # define the input nodes
        old_inputs = old_config.get("inputs", [])
        new_config["exec"] = self._calc_exec(old_inputs)

        return new_config
```

## 3. Executor (GraphExecutor)
Contains the core execution logic

```python
class SimpleNode(GenericExecutor):
    node_type = "simple_node"

    def __init__(self, initial_parameters, *args):
        super().__init__(initial_parameters)

    def initialize(self):
        pass

    # this is the value of the init configuration parameter
    def set_template(self, args):
        self.parameters = args

    def __call__(self, inputs, *args):
        output0 = inputs[0] + self.parameters[0]
        outputs = [output0]
        return outputs
```

