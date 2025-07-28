from modules.executors.common import BaseGuiNode


class AgentHistoryBuilderGui(BaseGuiNode):
    node_title = "Agent prompt builder"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("controller", "string");
        builder.addInput("tools", "string");
        builder.addInput("exec", "string");

        builder.addOutput("prompt", "string");
        builder.addOutput("GraphLLM", "string");
        builder.addOutput("variables", "string");

        builder.addStandardWidget("combo", "Tools", "markdown", None, {"property": "tools_format", "values": ["markdown", "json","python"]})
        builder.addStandardWidget("combo", "Agent", "ReAct(xml)", None, {"property": "agent_type", "values": ["ReAct(xml)"]})
        builder.addCustomWidget("textarea", "template", {"property": "template"})

        builder.setConnectionLimits({"max_outputs": 3, "min_outputs": 3, "min_inputs": 3})
        builder.setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

        builder.setPath("agent/agent_prompt_builder")

        return builder