# custom tools development

```
from modules.tool_call.common import GenericTool

class FakeWeather(GenericTool):
	tool_name = "fake weather"
	properties = {"default": False, "priority": 10}
```