from modules.executors.common import BaseGuiNode


class WebsocketClientGui(BaseGuiNode):
    node_title="Websocket client"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("send","string");
        builder.addOutput("receive","string");
        
        builder.addCustomWidget ("text_input","address",{ "property": "address"})
        builder.setPath("network/websocket_client")
        return builder

class WebsocketServerGui(BaseGuiNode):
    node_title="Websocket server"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("send","string");
        builder.addOutput("receive","string");
        
        options = { "min": 1, "max": 65535, "step": 10, "precision": 0, "property": "port" }
        builder.addStandardWidget("number","port", 8765, None, options )
        builder.setPath("network/websocket_server")
        return builder