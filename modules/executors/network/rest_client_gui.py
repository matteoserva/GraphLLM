from modules.executors.common import BaseGuiNode
from modules.executors.gui_node_builder import RawGuiArg

class RestClientGui(BaseGuiNode):
    node_title = "REST Client"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("data", "string")
        builder._addOutput("response", "string")
        
        builder._addCustomWidget("text_input", "URL", {"property": "url"})
        options = {"values": ["GET", "POST", "PUT", "DELETE", "PATCH"], "property": "method"}
        cb = RawGuiArg("""function(value, canvas, node, pos, event){
            if (value=="GET" || value=="DELETE")
            {    
                if( node.inputs.length > 0) {node.removeInput(0)}
            }
            else
            {
                if( node.inputs.length < 1) {node.addInput("data", "string")}
            }   
        }""")

        builder._addStandardWidget("combo", "Method", "GET", cb, options)

        builder._setPath("network/rest_client")
