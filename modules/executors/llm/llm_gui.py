from modules.executors.common import BaseGuiNode


class MyLLMCallNode(BaseGuiNode):
    node_title = "LLM Call"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in", "string");
        builder._addOutput("out", "string");
        builder._addOutput("json", "string");
        self._addSimpleProperty("conf", "")
        self._addSimpleProperty("template", "")
        builder._setConnectionLimits({"max_outputs":2, "min_outputs":2})

        builder._addStandardWidget("combo","subtype","stateless",None, { "property": "subtype", "values": ["stateless","stateful"] })

        builder._addCustomWidget("text_input","Config",{ "property": "conf"})
        builder._addCustomWidget("textarea","template",{ "property": "template"})
        builder._setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")
        builder._setPath("llm/llm_call")