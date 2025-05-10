from modules.executors.common import BaseGuiNode


class ImageGui(BaseGuiNode):
    node_title = "Image input"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addOutput("image", "string");
        builder._addCustomWidget("text_input", "name", {"property": "name", "default": ""})
        builder._addCustomWidget("image_drop", "image", {"property": "image"})

        builder._setPath("image_input")