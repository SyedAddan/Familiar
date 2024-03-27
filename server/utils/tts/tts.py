import numpy as np
import librosa
from IPython.display import Audio, display, clear_output
# import IPython
import sys
import os
import subprocess
# from scipy.io.wavfile import write
from pathlib import Path
from vocoder import inference as vocoder
from encoder import inference as encoder
from synthesizer.inference import Synthesizer
print(__path__)
sys.path.append(__path__[0])


project_name = "Real_Time_Voice_Cloning"
folder_path = 'saved_models\\default'
if not os.path.exists(folder_path):
    subprocess.run(f'mkdir saved_models\\default', shell=True)
    subprocess.run(
        f'cd saved_models/default/ && gdown https://drive.google.com/uc?id=1q8mEGwCkFy23KZsinbuvdKAQLqNKbYf1', shell=True)
    subprocess.run(
        f'cd saved_models/default/ && gdown https://drive.google.com/uc?id=1EqFMIbvxffxtjiVrtykroF6_mUh-5Z3s', shell=True)
    subprocess.run(
        f'cd saved_models/default/ && gdown https://drive.google.com/uc?id=1cf2NO6FtI0jDuy8AV3Xgn6leO6dHjIgu', shell=True)
    
sys.path.append(project_name)

encoder.load_model(
    Path("saved_models\\default\\encoder.pt"))
synthesizer = Synthesizer(
    Path("saved_models\\default\\synthesizer.pt"))
vocoder.load_model(
    Path("saved_models\\default\\vocoder.pt"))


SAMPLE_RATE = 22050

def compute_embedding(audio):
    display(Audio(audio, rate=SAMPLE_RATE, autoplay=True))
    embedding = encoder.embed_utterance(
        encoder.preprocess_wav(audio, SAMPLE_RATE))
    
    return embedding

def upload_audio_file(file_path):
    try:
        audio, _ = librosa.load(file_path, sr=SAMPLE_RATE)
        return audio
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def synthesize(text, path):
    audio_data = upload_audio_file(path)
    embedding = None
    if audio_data is not None:
        embedding = compute_embedding(audio_data)
    else:
        raise Exception("Error: Audio file not found")
    
    specs = synthesizer.synthesize_spectrograms([text], [embedding])
    generated_wav = vocoder.infer_waveform(specs[0])
    generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")
    # clear_output()
    # display(Audio(generated_wav, rate=synthesizer.sample_rate, autoplay=True))
    # output_file_path = "output_audio.wav"

    # Save the audio as a WAV file
    return synthesizer.sample_rate, generated_wav
    # write(output_file_path, synthesizer.sample_rate, generated_wav)
