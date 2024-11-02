import re
import sys
from piper.__main__ import main
import numpy as np
from piper import PiperVoice
from piper.download import ensure_voice_exists, find_voice, get_voices
import logging
import os
import wave
import io

#python3 -m modules.executors.tts.parla |aplay -r 16000 -f S16_LE -t raw -


PIPER_DIR = os.path.dirname(__file__)

class EngineTTS:
    def __init__(self):
        self.download_dir = PIPER_DIR
        self.synthesizer = None

    def load_voice(self, language):

        if os.path.exists(PIPER_DIR + "/voices.json"):
            all_voices = get_voices(self.download_dir,False)
        else:
            all_voices = get_voices(self.download_dir, True)
        filtered_voices = [el for el in all_voices if el.startswith(language)]
        selected_voice = filtered_voices[0]
        ensure_voice_exists(selected_voice,[self.download_dir],self.download_dir,all_voices)
        self.selected_voice = selected_voice
        self.synthesizer = PiperVoice.load(self.download_dir + "/" + selected_voice + ".onnx", config_path=None, use_cuda=False)
        
        return selected_voice

    def read_line(self, text):
        synthesize_args = {'speaker_id': None, 'length_scale': None, 'noise_scale': None, 'noise_w': None, 'sentence_silence': 0.7}
        audio_stream = self.synthesizer.synthesize_stream_raw(line, **synthesize_args)
        
        return audio_stream
    
    def read_text(self,text,sentence_silence=0.8):
        sentence_phonemes = self.synthesizer.phonemize(text)
        num_silence_samples = int(sentence_silence * self.synthesizer.config.sample_rate)
        silence_bytes = bytes(num_silence_samples * 2)
        synthesize_args = {'speaker_id': None, 'length_scale': None, 'noise_scale': None, 'noise_w': None}
        for phonemes in sentence_phonemes:
            #print("processing: ", "".join(phonemes), file=sys.stderr)
            phoneme_ids = self.synthesizer.phonemes_to_ids(phonemes)
            yield self.synthesizer.synthesize_ids_to_raw(phoneme_ids,**synthesize_args) + silence_bytes

    def read_text_to_buffers(self,line,sentence_silence=0.8):
        for audio_bytes in self.read_text(line):
            with io.BytesIO() as dest, wave.open(dest, "wb") as f:
                f.setnchannels(1)
                # 2 bytes per sample.
                f.setsampwidth(2)
                f.setframerate(self.synthesizer.config.sample_rate)
                f.writeframes(audio_bytes)
                val = dest.getvalue()
            yield val

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    engine = EngineTTS()
    selected_voice = engine.load_voice("it_IT-riccardo-x_low")

    lines = [
        "Da decenni il Libano fa i conti con una situazione politica, economica e sociale molto precaria, e al momento il paese non avrebbe i soldi né le risorse necessarie per rispondere a un’emergenza di questa portata. La situazione è diventata ancora più instabile in seguito all’uccisione da parte di Israele di Hassan Nasrallah, il leader del gruppo militare e politico libanese Hezbollah, avvenuta venerdì scorso con un bombardamento sulla capitale Beirut. "
        ]

    line = "Innaffiare le piante è un elemento cruciale per la loro crescita e sopravvivenza, poiché l'acqua è essenziale per tutte le funzioni vitali delle piante. L'acqua permette alle piante di trasportare i nutrienti dal suolo fino alle loro parti superiori, facilitando il processo di fotosintesi. Inoltre, aiuta a mantenere la struttura flessibile e rigida della pianta, permettendole di rimanere eretta. Senza una idratazione adeguata, le piante possono soffrire di stress idrico, che può portare a foglie secche e ammaccate, crescita rallentata, e in casi estremi, alla morte della pianta. Pertanto, è importante capire e rispettare i bisogni idrici specifici di ogni tipo di pianta per garantire la loro salute e la loro fioritura."

    #lines = ["Hello! How can I assist you today?"]

    for audio_bytes in engine.read_text(line):
        with io.BytesIO() as dest, wave.open(dest, "wb") as f:
            f.setnchannels(1)
            # 2 bytes per sample.
            f.setsampwidth(2)
            f.setframerate(16000)

            sys.stdout.buffer.write(audio_bytes)
            sys.stdout.buffer.flush()

            f.writeframes(audio_bytes)


            with open("/tmp/file.wav","wb") as f:
              val = dest.getvalue()
              f.write(val)