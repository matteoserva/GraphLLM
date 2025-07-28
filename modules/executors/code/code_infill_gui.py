from modules.executors.common import BaseGuiNode


class WebsocketClientGui(BaseGuiNode):
    node_title = "Code infill (WIP)"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        #builder._addInput("send", "string");
        builder.addOutput("LLM", "string");
        builder.addOutput("code", "string");
        builder.addCustomWidget("text_input", "repo_name", {"property": "repo_name", "default":"test"})

        builder.addCustomWidget("file_drop", "files", {"property": "files"})
        builder.setPath("text/code_infill")

        source_location = {"position": "output", "slot": 0, "filter": "llm_call"}
        eventId = {"type": "print"};
        action = {"type": "widget_action", "target": "append", "property": "files"}
        builder.subscribe(source_location, eventId, action)

        source_location = {"position": "output", "slot": 0, "filter": "llm_call"}
        eventId = {"type": "starting"};
        action = {"type": "widget_action", "target": "reset", "property": "files"}
        builder.subscribe(source_location, eventId, action)

        source_location = {"position": "output", "slot": 0, "filter": "llm_call"}
        eventId = {"type": "output", "slot": 0};
        action = {"type": "widget_action", "target": "set", "property": "files"}
        builder.subscribe(source_location, eventId, action)

        return builder