from modules.executors.common import BaseGuiNode


class AgentHistoryBuilderGui(BaseGuiNode):
    node_title = "Agent history builder"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in", "string");
        builder._addOutput("out", "string");

        builder._setPath("agent/agent_history_builder")