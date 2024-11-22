from modules.executors.common import BaseGuiNode


class WebsocketClientGui(BaseGuiNode):
    node_title = "Code infill"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("send", "string");
        builder._addOutput("receive", "string");

        builder._addCustomWidget("file_drop", "files", {"property": "files"})
        builder._setPath("text/code_infill")
