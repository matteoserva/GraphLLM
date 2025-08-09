from modules.executors.common import BaseGuiNode

class AppendGui(BaseGuiNode):
    node_type = "text_append"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");

        builder.addCustomWidget("textarea","",{ "property": "textarea"})


        return builder


from modules.executors.common import BaseGuiParser

class AppendParser(BaseGuiParser):
    node_types = ["text_append"]



from modules.executors.common import GenericExecutor

class AppendNode(GenericExecutor):
    node_type = "text_append"

    def __call__(self, inputs, *args):
        textarea_value = self.properties["textarea"]
        output0 = inputs[0] + textarea_value
        outputs = [output0]
        return outputs