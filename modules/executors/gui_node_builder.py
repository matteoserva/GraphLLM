import json

class GuiNodeBuilder:
    def _reset(self):
        self.config = {"class_name": "", "node_type": "",
                       "title": "", "gui_node_config": {},
                       "callbacks": [], "inputs": [], "outputs": [],
                       "standard_widgets": [], "custom_widgets": [],
                       "properties": {}, "subscriptions" : []}

    def _setPath(self, nodeType):
        self.config["class_name"] = type(self).__name__
        self.config["node_type"] = nodeType
        self.config["title"] = self.node_title

    def _setConnectionLimits(self, limits):
        self.config["gui_node_config"]["connection_limits"] = limits

    def _setCallback(self, cbName, cbString):
        self.config["callbacks"].append((cbName, cbString))

    def _addInput(self, name, type="string"):
        self.config["inputs"].append((name, type))

    def _addOutput(self, name, type="string"):
        self.config["outputs"].append((name, type))

    def _addCustomWidget(self, *args):
        # print("custom widget:",args)
        self.config["custom_widgets"].append(args)

    def _addStandardWidget(self, *args):
        # print("standard widget:",args)
        if len(args) > 4 and isinstance(args[4], dict):
            options = args[4]
            if "property" in options and len(options["property"]) > 0:
                property_name = options["property"]
                default_value = args[2]
                self.config["properties"][property_name] = default_value

        self.config["standard_widgets"].append(args)

    def _subscribeSimple(self, event_id,*args):
        self.config["subscriptions"].append((event_id,args))




    def _makeHeader(self):

        res = f"""
        var LiteGraph = global.LiteGraph;
        /* ********************** *******************   
                {self.config["class_name"]}: {self.config["title"]}
         ********************** *******************  */
        //node constructor class
        """
        return res

    def _makeConstructor(self):
        res = ""

        for el in self.config["inputs"]:
            res += f'        this.addInput("{el[0]}","{el[1]}");\n'
        for el in self.config["outputs"]:
            res += f'        this.addOutput("{el[0]}","{el[1]}");\n'
        if len(self.config["gui_node_config"]) > 0:
            res += "        this.gui_node_config = " + json.dumps(self.config["gui_node_config"])

        # add properties
        if len(self.config["properties"]):
            res += "        this.properties = " + str(self.config["properties"]) + "\n"

        # add widgets

        for el in self.config["standard_widgets"]:
            res += "        this.addWidget(" + json.dumps(el)[1:-1] + ")\n"

        if len(self.config["custom_widgets"]) > 0:
            res += "        this.container = new DivContainer(this)\n"
            res += "        this.addCustomWidget( this.container);\n"
        for el in self.config["custom_widgets"]:
            res += "        this.container.addWidget" + str(el) + "\n"

        # add variables
        if len(self.config["subscriptions"]) > 0:
            res += "        this.history = {};" + "\n"

        res = "\n".join([" "*12 + el.strip() for el in res.split("\n")])
        res = """
        function """ + self.config["class_name"] + """()
        {\n""" + res + """
        
        }\n\n"""

        return res

    def _makeSubscriptions(self):
        res = ""
        if len(self.config["subscriptions"]) > 0:
            res += "        " + self.config["class_name"] + ".prototype.connectPublishers = function(subscribe) {\n"
        for eventId, actionData in self.config["subscriptions"]:
            eventType = eventId["type"]
            source_location = eventId["source"]
            actionType,parameter = actionData

            res += f'        this.history["{parameter}"] = ""\n'
            if source_location[0].lower()=="input":
                res += f"        var source_node = this.getInputNode({source_location[1]});\n"
            res += "        if(source_node) {\n"
            res += '        var eventId = {type: "' + eventType + '", source: source_node.id.toString()'
            if "slot" in eventId:
                res += ', slot: ' + str(eventId["slot"])
            res += '};\n'
            res += "        subscribe(eventId ,(eventId, eventData) => {"
            if(actionType == "append"):
                res += '        this.history["' + parameter + '"] += eventData;\n'
                res += '        this.container.setValue("' + parameter + '", this.history["' + parameter + '"])'
            elif(actionType == "set"):
                res += '        this.container.setValue("' + parameter + '", eventData);'
                res += '        this.history["' + parameter + '"] = eventData;'
            elif (actionType == "reset"):
                res += '        this.history["' + parameter + '"] = "";'
            res += "})\n"
            res += "        }\n\n"
            #res += str((eventType,source_location, actionType,parameter)) + "\n"
        if len(self.config["subscriptions"]) > 0:
            res += "        }\n\n"
        return res

    def _getNodeString(self):

        res = self._makeHeader()
        res += self._makeConstructor()
        res += self._makeSubscriptions()


        res += '        {ClassName}.title = "{title}"\n'.replace("{ClassName}",self.config["class_name"]).replace("{title}",self.config["title"])
        for el in self.config["callbacks"]:
            res += f'        {self.config["class_name"]}.prototype.{el[0]} = {el[1]}\n'

        res += f'        LiteGraph.registerNodeType("{self.config["node_type"]}", {self.config["class_name"]} );\n\n'


        final = """(function(global) {
        {content}
        })(this);\n\n""".replace("{content}",res)


        return final

