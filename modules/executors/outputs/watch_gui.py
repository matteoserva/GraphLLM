from modules.executors.common import BaseGuiNode


class WatchNodeGui(BaseGuiNode):
    node_title = "Watch"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self
        builder._reset()
        builder._addInput("in", "string");

        builder._addCustomWidget("text_output", "", {"property": "parameters"})
        builder._setPath("output/watch")

        source_location = {"position": "input", "slot": 0}
        eventId = {"type": "output"};
        action = {"type": "container_action", "target": "set", "parameter": "parameters"}
        builder._subscribe(source_location, eventId, action)

        source_location = {"position": "input", "slot": 0}
        eventId = {"type": "print"};
        action = {"type": "container_action", "target": "append", "parameter": "parameters"}
        builder._subscribe(source_location, eventId, action)

        source_location = {"position": "input", "slot": 0}
        eventId = {"type": "starting"};
        action = {"type": "container_action", "target": "reset", "parameter": "parameters"}
        builder._subscribe(source_location, eventId, action)