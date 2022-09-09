import torch
import torchaudio
from datasets import load_dataset,Audio
from transformers import Wav2Vec2ForCTC,Wav2Vec2Processor
import argparse
import tempfile
import queue
import sys

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

from tflite_support.task import audio
from tflite_support.task import core
from tflite_support.task import processor


processor_hindi = Wav2Vec2Processor.from_pretrained("theainerd/Wav2Vec2-large-xlsr-hindi")
model = Wav2Vec2ForCTC.from_pretrained("theainerd/Wav2Vec2-large-xlsr-hindi")
resampler = torchaudio.transforms.Resample(48_000, 16_000)

processor_english = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model_english = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

base_options = core.BaseOptions(file_name="/Users/sid/Desktop/Code/Shloka/Development/converted_tflite/soundclassifier_with_metadata.tflite")
classification_options = processor.ClassificationOptions(max_results=2)
options = audio.AudioClassifierOptions(base_options=base_options, classification_options=classification_options)
classifier = audio.AudioClassifier.create_from_options(options)


def record_audio(record_time=5):
    samplerate = 44100  # Hertz
    duration = record_time  # seconds
    filename = 'player_recordings/output.wav'
    mydata = sd.rec(int(samplerate * duration), samplerate=samplerate,
                    channels=1, blocking=True)
    sf.write(filename, mydata, samplerate)
    return filename
    print('[INFO] Finished recording audio')




def speechToHindi(audio_file):
    speech_array, sampling_rate = torchaudio.load(audio_file)
    speech = resampler(speech_array).squeeze().numpy()
    inputs = processor_hindi(speech, sampling_rate=16_000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    predicted_ids = torch.argmax(logits, dim=-1)

    print("Prediction:", processor_hindi.batch_decode(predicted_ids))
    return processor_hindi.batch_decode(predicted_ids)
    
def speechToEnglish(audio_file):
    speech_array, sampling_rate = torchaudio.load(audio_file)
    speech = resampler(speech_array).squeeze().numpy()
    input_values = processor_english(speech, return_tensors="pt", padding="longest").input_values  # Batch size 1

    # retrieve logits
    logits = model_english(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor_english.batch_decode(predicted_ids)
    return transcription


# Imports
def audio_classification(audio_file):
    audio_file = audio.TensorAudio.create_from_wav_file("/Users/sid/Desktop/Code/Shloka/Development/player_recordings/output.wav", classifier.required_input_buffer_size)
    audio_result = classifier.classify(audio_file)
    return audio_result
