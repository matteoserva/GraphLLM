from modules.executors.common import BaseGuiNode


class AgentControllerGui(BaseGuiNode):
    node_title = "Agent controller"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in", "string");
        builder._addOutput("out", "string");
        builder._addInput("tool result", "string");
        builder._addOutput("tool params", "string");

        builder._setPath("agent/agent_controller")

        return builder