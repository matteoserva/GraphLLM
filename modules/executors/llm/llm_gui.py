from modules.executors.common import BaseGuiNode


class MyLLMCallNode(BaseGuiNode):
    node_title = "LLM Call"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");
        builder.addOutput("json", "string");
        builder.addSimpleProperty("conf", "")
        builder.addSimpleProperty("template", "")
        builder.setConnectionLimits({"max_outputs":2, "min_outputs":2})

        builder.addStandardWidget("combo","subtype","stateless",None, { "property": "subtype", "values": ["stateless","stateful"] })

        builder.addCustomWidget("text_input","Config",{ "property": "conf"})
        builder.addCustomWidget("textarea","template",{ "property": "template"})
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")
        builder.setPath("llm/llm_call")

        return builder