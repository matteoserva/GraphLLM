import re
import sys
from piper.__main__ import main
import numpy as np
from piper import PiperVoice
from piper.download import ensure_voice_exists, find_voice, get_voices
import logging
import os

#python3 -m modules.executors.tts.parla |aplay -r 16000 -f S16_LE -t raw -

logging.basicConfig(level=logging.DEBUG)
PIPER_DIR = os.path.dirname(__file__)

class EngineTTS:
    def __init__(self):
        self.download_dir = PIPER_DIR
        self.synthesizer = None

    def load_voice(self, language):
        
        all_voices = get_voices(self.download_dir,False)
        filtered_voices = [el for el in all_voices if el.startswith(language)]
        selected_voice = filtered_voices[0]
        ensure_voice_exists(selected_voice,[self.download_dir],self.download_dir,all_voices)
        self.selected_voice = selected_voice
        self.synthesizer = PiperVoice.load(self.download_dir + "/" + selected_voice + ".onnx", config_path=None, use_cuda=False)
        
        return selected_voice

    def read_line(self, text):
        synthesize_args = {'speaker_id': None, 'length_scale': None, 'noise_scale': None, 'noise_w': None, 'sentence_silence': 0.0}
        audio_stream = self.synthesizer.synthesize_stream_raw(line, **synthesize_args)
        
        return audio_stream
        
engine = EngineTTS()
selected_voice = engine.load_voice("it_IT-riccardo-x_low")

lines = [
    "Da decenni il Libano fa i conti con una situazione politica, economica e sociale molto precaria, e al momento il paese non avrebbe i soldi né le risorse necessarie per rispondere a un’emergenza di questa portata.",
    "La situazione è diventata ancora più instabile in seguito all’uccisione da parte di Israele di Hassan Nasrallah, il leader del gruppo militare e politico libanese Hezbollah, avvenuta venerdì scorso con un bombardamento sulla capitale Beirut."
    ]

#lines = ["Hello! How can I assist you today?"]
for line in lines:
    audio_stream = engine.read_line(line)
    for audio_bytes in audio_stream:
        sys.stdout.buffer.write(audio_bytes)
        sys.stdout.buffer.flush()
    zeros = np.zeros(12000).astype(np.int16)
    sys.stdout.buffer.write(zeros)
    sys.stdout.buffer.flush()
