from modules.executors.common import BaseGuiNode


class AgentHistoryBuilderGui(BaseGuiNode):
    node_title = "Agent history builder"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("controller", "string");
        builder._addInput("tools", "string");
        builder._addOutput("variables", "string");

        builder._addStandardWidget("combo","Tools","markdown",None, { "property": "tools_format", "values": ["markdown"] })
        builder._addStandardWidget("combo","Agent","ReAct(xml)",None, { "property": "agent_type", "values": ["ReAct(xml)"] })

        builder._setPath("agent/agent_history_builder")