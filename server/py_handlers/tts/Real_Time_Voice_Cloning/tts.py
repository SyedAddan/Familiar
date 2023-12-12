import numpy as np
import librosa
from IPython.display import Audio, display, clear_output
import IPython
import sys
import os
import io
from scipy.io.wavfile import write
from os.path import exists, join, basename, splitext
project_name = "Real_Time_Voice_Cloning"
if True:
    sys.path.append(project_name)
    # print(1)
    from pathlib import Path
    from vocoder import inference as vocoder
    from encoder import inference as encoder
    from synthesizer.inference import Synthesizer
    import numpy as np
    import ipywidgets as widgets
    from IPython.utils import io
    from IPython.display import display, Audio, clear_output

    encoder.load_model(
        Path("saved_models\\default\\encoder.pt"))
    synthesizer = Synthesizer(
        Path("saved_models\\default\\synthesizer.pt"))
    vocoder.load_model(
        Path("saved_models\\default\\vocoder.pt"))


SAMPLE_RATE = 22050


def compute_embedding(audio):
    display(Audio(audio, rate=SAMPLE_RATE, autoplay=True))
    global embedding
    embedding = None
    embedding = encoder.embed_utterance(
        encoder.preprocess_wav(audio, SAMPLE_RATE))


def record_audio_seconds(seconds):
    audio = np.zeros(seconds * SAMPLE_RATE)
    mic = IPython.display.Audio(data=audio, rate=SAMPLE_RATE, autoplay=True)
    display(mic)
    return np.array(mic.data)


def upload_audio_file(file_path):
    try:
        audio, _ = librosa.load(file_path, sr=SAMPLE_RATE)
        return audio
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


record_or_upload = "Upload"  # Change to "Record" if you want to record audio
record_seconds = 10  # Adjust the duration if recording

if record_or_upload == "Record":
    audio_data = record_audio_seconds(record_seconds)
    compute_embedding(audio_data)
else:
    # Provide your audio file path here
    audio_file_path = "Recording.wav"
    audio_data = upload_audio_file(audio_file_path)
    if audio_data is not None:
        print("success")
        compute_embedding(audio_data)

# @title Synthesize a text { run: "auto" }
# @param {type:"string"}
text = "One of the two people who tested positive for the novel coronavirus in the United Kingdom is a student at the University of York in northern England."


def synthesize(embed, text):
    print("Synthesizing new audio...")
    # with io.capture_output() as captured:
    specs = synthesizer.synthesize_spectrograms([text], [embed])
    generated_wav = vocoder.infer_waveform(specs[0])
    generated_wav = np.pad(
        generated_wav, (0, synthesizer.sample_rate), mode="constant")
    clear_output()
    display(Audio(generated_wav, rate=synthesizer.sample_rate, autoplay=True))
    output_file_path = "output_audio.wav"

    # Save the audio as a WAV file
    write(output_file_path, synthesizer.sample_rate, generated_wav)


if embedding is None:
    print("first record a voice or upload a voice file!")
else:
    synthesize(embedding, text)
