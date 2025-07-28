from modules.executors.common import BaseGuiNode


class WatchNodeGui(BaseGuiNode):
    node_title = "Watch"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()
        builder._reset()
        builder._addInput("in", "string");

        builder._addCustomWidget("text_output", "", {"property": "parameters"})
        builder._setPath("output/watch")

        source_location = {"position": "input", "slot": 0}
        eventId = {"type": "output"};
        action = {"type": "widget_action", "target": "set", "property": "parameters", "silent": True}
        builder._subscribe(source_location, eventId, action)

        #source_location = {"position": "input", "slot": 0}
        #eventId = {"type": "print"};
        #action = {"type": "widget_action", "target": "append", "property": "parameters"}
        #builder._subscribe(source_location, eventId, action)
        builder._setCallback("onExecute", """function(){var val =this.getInputData(0); if(val) this.container.setValue("parameters",""+val)}""")

        source_location = {"position": "input", "slot": 0}
        eventId = {"type": "starting"};
        action = {"type": "widget_action", "target": "reset", "property": "parameters"}
        builder._subscribe(source_location, eventId, action)
        return builder