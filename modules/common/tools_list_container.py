import json

class ToolsListContainer():
    def __init__(self,tools_list, print_format="native"):
        self.tools_list = tools_list
        self.print_format = print_format

    def __str__(self):
        return self.getFormattedOps(self.print_format)

    def _format_tools_markdown(self,tools,namespace):
        ops = [el for el in tools]
        textlist = []
        for op in ops:
            row = ""
            row = row + "- " + namespace + op["name"]
            if op["doc"] is not None:
                row = row + ": " + op["doc"]
            param_names = [el["name"] for el in op["params"]]
            params_string = ",".join(param_names)
            if row[-1] == ".":
                row = row[:-1]
            row = row + ". Parameters: " + params_string
            textlist.append(row)
        res = "\n".join(textlist)
        return res

    def _format_tools_json(self,tools,namespace):
        #{"type": "function", "function": {"name": "get_current_temperature", "description": "Get current temperature at a location.", "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "The location to get the temperature for, in the format \"City, State, Country\"."}, "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "The unit to return the temperature in. Defaults to \"celsius\"."}}, "required": ["location"]}}}
        ops = [el for el in tools]
        textlist = []
        for op in ops:
            row = {"type":"function"}
            function = {"name": namespace + op["name"]}
            row["function"] = function

            if op["doc"] is not None:
                function["description"] = op["doc"]
            parameters = {"type":"object"}
            function["parameters"] = parameters
            properties = [el["name"] for el in op["params"]]
            parameters["properties"] = properties
            required = [el["name"] for el in op["params"] if el["required"]]
            parameters["required"] = required
            rowstring = json.dumps(row)
            textlist.append(rowstring)
        res = "\n".join(textlist)
        return res

    def _format_tools_python(self,tools,namespace):
        ops = [el for el in tools]
        textlist = []
        for op in ops:
            row = ""
            row += "def " + namespace + op["name"] + "("
            param_elements = []
            for el in op["params"]:
                param_elem = el["name"]
                if "type" in el:
                    param_elem += ": " + el["type"]
                if not el["required"]:
                    param_elem += " = " + el["default"]
                param_elements.append(param_elem)

            params_string = ", ".join(param_elements)
            row += params_string + ")"
            if "type" in op:
                row += " -> " + op["type"]
            row += ":\n"
            if op["doc"] is not None:
                row += '    """' + op["doc"] + '"""\n'
            textlist.append(row)
        res = "\n".join(textlist)
        return res

    def _format_tools(self,tools,format, namespace):
        if format == "json":
            res = self._format_tools_json(tools,namespace)
        elif format == "python":
            res = self._format_tools_python(tools,namespace)
        elif format == "markdown":
            res = self._format_tools_markdown(tools, namespace)
        else:
            res = str(tools)
        return res

    def getFormattedOps(self,format=None, namespace=""):
        return self._format_tools(self.tools_list, format, namespace)