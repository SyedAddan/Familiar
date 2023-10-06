from io import BytesIO
import torch
from glob import glob

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en',
                                       device=device)

(read_batch, split_into_batches, read_audio, prepare_model_input) = utils

def generate_text_from_speech(audioBlob):
    text = ""
    audio_buffer = BytesIO(audioBlob.read())

    # Save the audio data as a WAV file (or any other supported format)
    with open('audio.wav', 'wb') as audio_file:
        audio_file.write(audio_buffer.getvalue())
    test_files = glob('./audio.wav')
    batches = split_into_batches(test_files, batch_size=10)
    speech = prepare_model_input(read_batch(batches[0]), device=device)

    text = model(speech)
    for example in text:
        text = decoder(example.cpu())
    
    return text