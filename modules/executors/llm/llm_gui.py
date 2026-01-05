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

        panel = builder.addCustomWidget("panel","Config",{ "property": "extra_config"})
        panel.addCustomWidget("text_input","chat_template_kwargs",{ "property": "chat_template_kwargs", "format": "json"})
        panel.addCustomWidget("text_input", "Grammar", {"property": "grammar",})
        panel.addCustomWidget("text_input", "Client", {"property": "client", })
        panel.addCustomWidget("text_input", "Temperature", {"property": "temperature" , "format": "json"})
        panel.addCustomWidget("text_input", "Stopping words", {"property": "stop", "format": "json"})
        # panel.addCustomWidget("text_input", "Test3", {"property": "test3"})
        # panel.addCustomWidget("toggle", "Test4", {"property": "test4"})

        builder.addCustomWidget("text_input","Extra Config",{ "property": "conf"})
        builder.addCustomWidget("textarea","template",{ "property": "template"})
        
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")
        builder.setPath("llm/llm_call")

        return builder