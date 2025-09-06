from modules.executors.common import BaseGuiNode


class UDPSenderGui(BaseGuiNode):
    node_title = "UDP Sender"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("message", "string")
        builder.addCustomWidget ("text_input","ip",{ "property": "ip", "default": "127.0.0.1"})

        options = {"min": 1, "max": 65535, "step": 10, "precision": 0, "property": "port"}
        builder.addStandardWidget("number", "port", 8765, None, options)
        builder.setPath("udp_sender")
        return builder


class UDPReceiverGui(BaseGuiNode):
    node_title = "UDP Receiver"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addOutput("message", "string")
        options = {"min": 1, "max": 65535, "step": 10, "precision": 0, "property": "port"}
        builder.addCustomWidget("text_input", "ip", {"property": "ip", "default": "0.0.0.0"})
        builder.addStandardWidget("number", "port", 8765, None, options)
        options = {"min": 0, "step": 10, "precision": 0, "property": "iterations"}
        builder.addStandardWidget("number", "iterations", 1, None, options)
        builder.setPath("udp_receiver")
        return builder