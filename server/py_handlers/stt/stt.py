from io import BytesIO
import torch
import os

from glob import glob
from werkzeug.utils import secure_filename
import subprocess


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en',
                                       device=device)

(read_batch, split_into_batches, read_audio, prepare_model_input) = utils


def generate_text_from_speech(audioBlob):
    # import os

    # Replace with the path to the folder you want to work with
    folder_path = '..\\server'
    extension_to_delete = 'blob.wav' and 'output.wav'

    # List all files in the folder
    files = os.listdir(folder_path)

    # Loop through the files and delete files with the specified extension
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file.endswith(extension_to_delete):
            os.remove(file_path)

    # text = "Hello"
    file = audioBlob
    # UPLOAD_FOLDER = 'audios'
    if file:
        # Ensure the filename has a .wav extension
        if not file.filename.endswith('.wav'):
            file.filename = secure_filename(file.filename) + ".wav"

        file.save(os.path.join(file.filename))

    audio_buffer = BytesIO(audioBlob.read())

    # Define the FFmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-i', 'blob.wav',       # Input file name
        '-acodec', 'pcm_s16le',  # Audio codec (PCM 16-bit little-endian)
        '-ar', '44100',          # Sample rate (44100 Hz)
        '-ac', '2',              # Number of audio channels (2 for stereo)
        'output.wav'             # Output file name
    ]

    # Execute the FFmpeg command
    try:
        subprocess.run(ffmpeg_command, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Audio file conversion completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during audio file conversion: {e.returncode}")
        print(e.stderr.decode())

    # You can now continue with your Python script using the converted 'output.wav' file.

    test_files = glob(
        '..\\server\\output.wav')

    batches = split_into_batches(test_files, batch_size=10)
    speech = prepare_model_input(read_batch(batches[0]), device=device)

    text = model(speech)
    for example in text:
        text = decoder(example.cpu())
    return text
    # Save the audio data as a WAV file (or any other supported format)
    # with open('audio.wav', 'wb') as audio_file:
    #     audio_file.write(audio_buffer.getvalue())
