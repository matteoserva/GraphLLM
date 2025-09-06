from modules.executors.common import BaseGuiNode


class AgentControllerGui(BaseGuiNode):
    node_title = "Agent controller"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("out", "string");
        builder.addInput("tool raw", "string");
        builder.addOutput("tool params", "string");

        builder.setPath("agent/agent_controller")

        return builder