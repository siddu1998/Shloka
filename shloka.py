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

processor = Wav2Vec2Processor.from_pretrained("theainerd/Wav2Vec2-large-xlsr-hindi")
model = Wav2Vec2ForCTC.from_pretrained("theainerd/Wav2Vec2-large-xlsr-hindi")
resampler = torchaudio.transforms.Resample(48_000, 16_000)

processor_english = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model_english = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")
  

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument(
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args(remaining)

q = queue.Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())



def record_player_audio(): 
    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])
        if args.filename is None:
            args.filename = tempfile.mktemp(prefix="chant",suffix='.wav', dir='player_recordings')

        # Make sure the file is opened before recording anything:
        with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
                        channels=args.channels, subtype=args.subtype) as file:
            with sd.InputStream(samplerate=args.samplerate, device=args.device,
                                channels=args.channels, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                while True:
                    file.write(q.get())
    except KeyboardInterrupt:
        print('\nRecording finished: ' + repr(args.filename))
        return args.filename
        #parser.exit(0)
    except Exception as e:
      print('Some Error in Audio recoding')
      #parser.exit(type(e).__name__ + ': ' + str(e))



def speechToHindi(audio_file):
    speech_array, sampling_rate = torchaudio.load(audio_file)
    speech = resampler(speech_array).squeeze().numpy()
    inputs = processor(speech, sampling_rate=16_000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    predicted_ids = torch.argmax(logits, dim=-1)

    print("Prediction:", processor.batch_decode(predicted_ids))
    return processor.batch_decode(predicted_ids)
    
def speechToEnglish(audio_file):
    speech_array, sampling_rate = torchaudio.load(audio_file)
    speech = resampler(speech_array).squeeze().numpy()
    input_values = processor_english(speech, return_tensors="pt", padding="longest").input_values  # Batch size 1

    # retrieve logits
    logits = model_english(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor_english.batch_decode(predicted_ids)
    return transcription






  


