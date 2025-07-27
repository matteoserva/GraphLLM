from modules.executors.gui_node_builder import GuiNodeBuilder

class BaseGuiNode(GuiNodeBuilder):

    def buildNode(self):
        builder = self._initBuilder()
        return builder

