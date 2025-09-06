from modules.executors.common import BaseGuiNode


class ImageGui(BaseGuiNode):
    node_title = "Image input"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addOutput("image", "string");
        builder.addCustomWidget("text_input", "name", {"property": "name", "default": ""})
        builder.addCustomWidget("image_drop", "image", {"property": "image"})

        builder.setPath("image_input")

        return builder