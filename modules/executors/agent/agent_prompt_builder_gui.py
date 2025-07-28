from modules.executors.common import BaseGuiNode


class AgentHistoryBuilderGui(BaseGuiNode):
    node_title = "Agent prompt builder"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("controller", "string");
        builder._addInput("tools", "string");
        builder._addInput("exec", "string");

        builder._addOutput("prompt", "string");
        builder._addOutput("GraphLLM", "string");
        builder._addOutput("variables", "string");

        builder._addStandardWidget("combo", "Tools", "markdown", None, {"property": "tools_format", "values": ["markdown", "json","python"]})
        builder._addStandardWidget("combo", "Agent", "ReAct(xml)", None, {"property": "agent_type", "values": ["ReAct(xml)"]})
        builder._addCustomWidget("textarea", "template", {"property": "template"})

        builder._setConnectionLimits({"max_outputs": 3, "min_outputs": 3, "min_inputs": 3})
        builder._setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

        builder._setPath("agent/agent_prompt_builder")

        return builder