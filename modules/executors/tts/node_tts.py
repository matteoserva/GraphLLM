from ..common import GenericExecutor
from .parla import EngineTTS

class TTSNode(GenericExecutor):
    node_type = "tts"

    def __init__(self, node_graph_parameters):
        super().__init__(node_graph_parameters)

    def initialize(self):
        self. engine = EngineTTS()
        selected_voice = self.engine.load_voice("it_IT-riccardo-x_low")

    def set_parameters(self, args):
        pass

    def __call__(self, *args):
        for el in self.engine.read_text_to_buffers(args[0][0]):
            self.node.log("audio", {}, el)
        return []