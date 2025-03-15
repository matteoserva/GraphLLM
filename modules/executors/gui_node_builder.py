import json

_template_global = """\
(function(global) {
     {content}
})(this);
"""

class GuiNodeBuilder:
    def _reset(self):
        self.config = {"class_name": "", "node_type": "",
                       "title": "", "gui_node_config": {},
                       "callbacks": [], "inputs": [], "outputs": [],
                       "standard_widgets": [], "custom_widgets": [], "titlebar_widgets" : [],
                       "properties": {}, "subscriptions" : [], "extra_properties": []}

    def _setPath(self, nodeType):
        self.config["class_name"] = type(self).__name__
        self.config["node_type"] = nodeType
        self.config["title"] = self.node_title

    def _setConnectionLimits(self, limits):
        self.config["gui_node_config"]["connection_limits"] = limits
        self._setCallback("onConnectionsChange", "MyGraphNode.prototype.onConnectionsChange")

    def _setCallback(self, cbName, cbString):
        if cbName in ["onConnectionsChange"]:
            cb_names = [el[0] for el in self.config["callbacks"]]
            if cbName in cb_names:
                self.config["callbacks"] = [el for el in self.config["callbacks"] if el[0] != cbName]
        self.config["callbacks"].append((cbName, cbString))

    def _addInput(self, name, type="string"):
        self.config["inputs"].append((name, type))

    def _addOutput(self, name, type="string"):
        self.config["outputs"].append((name, type))

    def _addCustomWidget(self, *args):
        # print("custom widget:",args)
        self.config["custom_widgets"].append(args)

    def _addTitlebarWidget(self, *args):
        # print("custom widget:",args)
        self.config["titlebar_widgets"].append(args)

    def _addSimpleProperty(self,property_name,default_value):
        self.config["properties"][property_name] = default_value

    def _addStandardWidget(self, *args):
        # print("standard widget:",args)
        if len(args) > 4 and isinstance(args[4], dict):
            options = args[4]
            if "property" in options and len(options["property"]) > 0:
                property_name = options["property"]
                default_value = args[2]
                self._addSimpleProperty(property_name,default_value)

            if args[0] == "combo" and "property" in options and len(options["property"]) >0 and len(options.get("values",[])) > 0:
                extra_property = [args[1], args[2], "enum", {"values": options["values"]} ]
                self.config["extra_properties"].append(extra_property)

        self.config["standard_widgets"].append(args)

    def _subscribe(self, *args):
        self.config["subscriptions"].append(args)




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
            res += "        this.gui_node_config = " + json.dumps(self.config["gui_node_config"]) + "\n"

        # add properties
        if len(self.config["properties"]):
            res += "        this.properties = " + str(self.config["properties"]) + "\n"
            for el in self.config["extra_properties"]:
                res += "            this.addProperty(" + json.dumps(el)[1:-1] + ");\n"

        # add widgets

        for el in self.config["standard_widgets"]:
            res += "        this.addWidget(" + json.dumps(el)[1:-1] + ")\n"

        if len(self.config["custom_widgets"]) > 0:
            res += "        this.container = new DivContainer(this)\n"
            res += "        this.addCustomWidget( this.container);\n"

        for el in self.config["custom_widgets"]:
            res += "        this.container.addWidget" + str(el) + "\n"

        if len(self.config["titlebar_widgets"]) > 0:
            res += "        this.addCustomWidget( new TitlebarContainer(this));\n"

        res = "\n".join([" "*12 + el.strip() for el in res.split("\n")])
        res = """
        function """ + self.config["class_name"] + """()
        {\n""" + res + """
        
        }\n\n"""

        return res

    def _makeSubscriptions(self):
        subscription_header = "{ClassName}.prototype.connectPublishers = function(subscribe) {"
        subscription_content= "subscribe(this,{parameters})"
        subscription_footer = "}"

        res = ""
        if len(self.config["subscriptions"]) > 0:
            val = " "*8 + subscription_header +"\n"
            res += val.replace("{ClassName}",self.config["class_name"])

        for subscription_info in self.config["subscriptions"]:
            val = " "*12 + subscription_content + "\n"
            res += val.replace("{parameters}",json.dumps(subscription_info)[1:-1])

        if len(self.config["subscriptions"]) > 0:
            val = " " * 8 + subscription_footer + "\n\n"
            res += val
        return res

    def _makePrototypes(self):
        res = ""
        for el in self.config["callbacks"]:
            res += f'        {self.config["class_name"]}.prototype.{el[0]} = {el[1]}\n'
        return res

    def _makeFooter(self):
        res = ""
        res += '        {ClassName}.title = "{title}"\n'.replace("{ClassName}", self.config["class_name"]).replace("{title}", self.config["title"])
        res += f'        LiteGraph.registerNodeType("{self.config["node_type"]}", {self.config["class_name"]} );\n\n'

        return res

    def _getNodeString(self):

        res = self._makeHeader()
        res += self._makeConstructor()
        res += self._makeSubscriptions()
        res += self._makePrototypes()
        res += self._makeFooter()

        final = _template_global

        final = final.replace("{content}",res)


        return final

