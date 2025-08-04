

The node parser reads a gui node and generates the backend node configuration.
It can return a single node or a list of nodes.
Work in progress. Right now use the default implementation:

```
from modules.executors.common import BaseGuiParser

class SimpleParser(BaseGuiParser):
    node_types = ["simple_gui"]


```