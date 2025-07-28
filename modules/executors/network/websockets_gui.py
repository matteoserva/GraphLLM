from modules.executors.common import BaseGuiNode


class WebsocketClientGui(BaseGuiNode):
    node_title="Websocket client"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("send","string");
        builder._addOutput("receive","string");
        
        builder._addCustomWidget ("text_input","address",{ "property": "address"})
        builder._setPath("network/websocket_client")
        return builder

class WebsocketServerGui(BaseGuiNode):
    node_title="Websocket server"

    def __init__(self):
        pass


    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("send","string");
        builder._addOutput("receive","string");
        
        options = { "min": 1, "max": 65535, "step": 10, "precision": 0, "property": "port" }
        builder._addStandardWidget("number","port", 8765, None, options )
        builder._setPath("network/websocket_server")
        return builder