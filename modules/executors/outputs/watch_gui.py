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

        event_id = {"type": "starting", "source": ("input",0)}
        builder._subscribeSimple(event_id, "reset", "parameters")
        event_id = {"type": "print", "source": ("input", 0)}
        builder._subscribeSimple(event_id, "append", "parameters")
        event_id = {"type": "output", "source": ("input", 0), "slot": 0}
        builder._subscribeSimple(event_id, "set", "parameters")