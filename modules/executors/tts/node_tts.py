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
        language = args.get("lang")
        self.engine.load_voice(language)

    def __call__(self, *args):
        text = args[0][0]

        phonemized = self.engine.phonemize(text)
        for phonemes in phonemized:
            display_val = "".join(phonemes)
            self.node.log("call", "display", display_val)
            audio = self.engine.read_phonemized_to_buffer(phonemes)
            self.node.log("audio", {}, audio)
        self.node.log("call", "display", text)
        return []