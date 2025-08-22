from modules.executors.common import BaseGuiNode

class SwitchGui(BaseGuiNode):
    """Compares the test case with the input and routes to corresponding output"""
    node_type = "text_switch_case"

    def __init__(self):
        pass

    def buildNode(self):
        builder = self._initBuilder()

        builder.addInput("in", "string");
        builder.addOutput("index", "string");
        builder.addOutput("default", "string");

        builder.addStandardWidget("combo", "Case insensitive", "YES", None, {"property": "case_insensitive", "values": ["NO", "YES"]})
        builder.addCustomWidget("list","Switch",{ "property": "cases"})
        builder.setConnectionLimits({"min_outputs": 2, "min_inputs": 1, "max_inputs": 1})
        builder.setTitle("Switch case")
        return builder


from modules.executors.common import BaseGuiParser

class SwitchParser(BaseGuiParser):
    node_types = ["text_switch_case"]

from modules.executors.common import GenericExecutor

class SwitchNode(GenericExecutor):
    node_type = "text_switch_case"

    def initialize(self):
        self.insensitive = True

    def set_parameters(self,args):
        self.insensitive = False if args["case_insensitive"] == "NO" else True
        self.test_cases = args["cases"]
        if self.insensitive:
            self.test_cases = [el.lower() for el in self.test_cases]

    def _find_match(self,input,test_cases):
        for index, case in enumerate(test_cases):
            if case in input:
                return index + 1
        return 0

    def __call__(self, inputs, *args):
        input = inputs[0]
        if self.insensitive:
            input = input.lower()

        match_index = self._find_match(input,self.test_cases)
        outputs = [None] * (2+match_index)
        outputs[0] = match_index
        outputs[1+match_index] = input

        return outputs