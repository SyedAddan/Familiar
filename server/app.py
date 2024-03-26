from flask import Flask, request, jsonify, send_file
import time
from scipy.io import wavfile
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
import io
import subprocess
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import soundfile as sf

from py_handlers.chatbot.chatbot import generate_chatbot_response
from py_handlers.stt.stt import generate_text_from_speech
from py_handlers.tts.tts.tts import synthesize

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True,
                         nullable=False, primary_key=True)
    avatarName = db.Column(db.String(80), unique=True, nullable=False)
    relationship = db.Column(db.String(1024), unique=False, nullable=False)
    additional = db.Column(db.String(1024), unique=False, nullable=True)
    password = db.Column(db.String(120), nullable=False)
    audio_path = db.Column(db.String(255), nullable=False)

    def __init__(self, email, username, avatarName, relationship, additional, password, audio_path):
        self.email = email
        self.username = username
        self.avatarName = avatarName
        self.relationship = relationship
        self.additional = additional
        self.password = password
        self.audio_path = audio_path


@app.route('/signupInputs', methods=['POST'])
def signUpHandler():
    try:
        email = request.form['email']
        username = request.form['username']
        avatarName = request.form['avatarName']
        relationship = request.form['relationship']
        additional = request.form['additional']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        voice = request.files['voice']

        print(email, username, avatarName, relationship,
              additional, password, confirmPassword, voice)

        folder_path = '..\\server'
        extension_to_delete = 'blob.wav' and 'output.wav'

        # List all files in the folder
        files = os.listdir(folder_path)

        # Loop through the files and delete files with the specified extension
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and file.endswith(extension_to_delete):
                os.remove(file_path)
        # Save the audio file to a server directory
        file = voice
        # UPLOAD_FOLDER = 'audios'
        if file:
            # Ensure the filename has a .wav extension
            if not file.filename.endswith('.wav'):
                file.filename = secure_filename(file.filename) + ".wav"

            file.save(os.path.join(file.filename))
        audio_buffer = BytesIO(voice.read())

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

        # Create a new User instance
        new_user = User(email=email, username=username, avatarName=avatarName,
                        relationship=relationship, additional=additional, password=password, audio_path="C:\\Users\\dortemon\\Downloads\\FYP\\Familiar\\server\\output.wav")

        # Add the User to the database and commit the changes
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"responseText": "Success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"responseText": "Something went wrong"}), 500


@app.route('/getUser', methods=['GET'])
def getUser():
    try:
        userName = request.args.get('userName')
        user = User.query.filter_by(username=userName).first()
        return jsonify({"username": user.username, "avatarName": user.avatarName, "relationship": user.relationship, "additional": user.additional}), 200
    except Exception as e:
        print(e)
        return jsonify({"responseText": "Something went wrong"}), 500


@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        message = data["message"]
        userName = data["userName"]
        avatarName = data["avatarName"]
        avatarRelationship = data["avatarRelation"]
        avatarAdditional = data["avatarAdditional"]
        start = time.time()
        res = generate_chatbot_response(
            message, avatarName, avatarRelationship, avatarAdditional)
        voice_path = Path.absolute(User.query.filter_by(
            username=userName, avatarName=avatarName).first().audio_path)
        sr, wav = synthesize(res, voice_path)

        wav_io = io.BytesIO()
        sf.write(wav_io, wav, sr, format='WAV')
        wav_io.seek(0)
        end = time.time()

        responceTime = end - start
        return jsonify({"responseText": res, 'audio': send_file(wav_io, as_attachment=True, download_name='generated_audio.wav'), "responceTime": responceTime}), 200
    except Exception as e:
        print(e)
        return jsonify({"responseText": "Something went wrong", "responceTime": 0}), 500


@app.route('/stt', methods=['POST'])
def stt():
    try:
        audioBlob = request.files['audio']
        text = generate_text_from_speech(audioBlob)
        return jsonify({'text': text}), 200
    except Exception as e:
        print(e)
        return jsonify({'text': 'Something went wrong'}), 500


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True, port=5000)
