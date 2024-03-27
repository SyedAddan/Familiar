import io
import time
import uvicorn
import soundfile as sf
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.llm.llm import generate_chatbot_response
# from utils.stt.stt import generate_text_from_speech


def handle_text_stream(res_stream):
    for event in res_stream:
        if "content" in event["choices"][0].delta:
            current_response = event["choices"][0].delta.content
            yield "data: " + current_response + "\n\n"

def messages_to_db_form(messages):
    str = ""
    for message in messages:
        str += "Role: " + message["role"] + \
            " Content: " + message["content"] + "/n"
    return str

def messages_from_db_form(message_str):
    if not message_str:
        return []
    else:
        messages = []
        for line in message_str.split("/n"):
            if line == "": continue
            role = line.split("Role: ")[1].split(" Content: ")[0].strip()
            content = line.split("Role: ")[1].split(" Content: ")[1].strip()
            messages.append({"role": role, "content": content})
        return messages

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False, primary_key=True)
    avatarName = Column(String(80), unique=True, nullable=False)
    relationship = Column(String(1024), unique=False, nullable=False)
    additional = Column(String(1024), unique=False, nullable=True)
    password = Column(String(120), nullable=False)
    audio_path = Column(String(255), nullable=False)
    messages = Column(String(10000), nullable=True)

app = FastAPI()

# Allowing CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/signupInputs')
async def signUpHandler(email: str, username: str, avatarName: str, relationship: str, additional: str, password: str, confirmPassword: str, voice: UploadFile = File(...)):
    try:
        # Save the audio file to a server directory
        voice_path = f"voices/{username}_{avatarName}_voice.wav"
        with open(voice_path, "wb") as audio_file:
            audio_file.write(await voice.read())

        # Create a new User instance
        new_user = User(email=email, username=username, avatarName=avatarName,
                        relationship=relationship, additional=additional, password=password, audio_path=voice_path, messages="")

        # Add the User to the database and commit the changes
        db.add(new_user)
        db.commit()

        return {"responseText": "Success"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")

@app.get('/getUser')
async def getUser(userName: str):
    try:
        user = db.query(User).filter_by(username=userName).first()
        return {
            "username": user.username,
            "avatarName": user.avatarName,
            "relationship": user.relationship,
            "additional": user.additional,
            "messages": messages_from_db_form(user.messages)
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")


class ChatbotRequest(BaseModel):
    message: str
    userName: str

@app.post('/chatbot')
async def chatbot(request_data: ChatbotRequest):
    try:
        userData = db.query(User).filter_by(username=request_data.userName).first()
        avatarName = userData.avatarName
        avatarRelationship = userData.relationship
        avatarAdditional = userData.additional
        messages = messages_from_db_form(userData.messages)
        response, messages = generate_chatbot_response(
            request_data.message,
            avatarName,
            avatarRelationship,
            avatarAdditional,
            messages
        )
        userData.messages = messages_to_db_form(messages)
        db.commit()
        
        return {'responseText': response}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")


# @app.post('/stt')
# async def stt(audio: UploadFile = File(...)):
#     try:
#         text = generate_text_from_speech(await audio.read())
#         return {'text': text}
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Something went wrong")


if __name__ == '__main__':
    engine = create_engine('sqlite:///users.sqlite3')
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    uvicorn.run(app, host="0.0.0.0", port=5000)










# import io
# import time
# import soundfile as sf
# from pathlib import Path
# from flask_cors import CORS
# from scipy.io import wavfile
# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask, request, jsonify, send_file, Response

# from utils.llm.llm import generate_chatbot_response
# from utils.stt.stt import generate_text_from_speech
# # from utils.tts.tts import synthesize

# app = Flask(__name__)
# CORS(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.app_context().push()
# db = SQLAlchemy(app)


# def handle_text_stream(res_stream):
#     for token in res_stream:
#         yield token


# def messages_to_db_form(messages):
#     str = ""
#     for message in messages:
#         str += "Role: " + message["role"] + \
#             " Content: " + message["content"] + "/n"

# def messages_from_db_form(message_str):
#     if message_str=='':
#         return []
#     else:
#         messages = []
#         for line in message_str.split("/n"):
#             role = line.split("Role: ")[1].split(" Content: ")[0].strip()
#             content = line.split("Role: ")[1].split(" Content: ")[1].strip()
#             messages.append({"role": role, "content": content})


# class User(db.Model):
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     username = db.Column(db.String(80), unique=True,
#                          nullable=False, primary_key=True)
#     avatarName = db.Column(db.String(80), unique=True, nullable=False)
#     relationship = db.Column(db.String(1024), unique=False, nullable=False)
#     additional = db.Column(db.String(1024), unique=False, nullable=True)
#     password = db.Column(db.String(120), nullable=False)
#     audio_path = db.Column(db.String(255), nullable=False)
#     messages = db.Column(db.String(10000), nullable=True)

#     def __init__(self, email, username, avatarName, relationship, password, audio_path, additional="", messages=""):
#         self.email = email
#         self.username = username
#         self.avatarName = avatarName
#         self.relationship = relationship
#         self.additional = additional
#         self.password = password
#         self.audio_path = audio_path
#         self.messages = messages


# @app.route('/signupInputs', methods=['POST'])
# def signUpHandler():
#     try:
#         email = request.form['email']
#         username = request.form['username']
#         avatarName = request.form['avatarName']
#         relationship = request.form['relationship']
#         additional = request.form['additional']
#         password = request.form['password']
#         confirmPassword = request.form['confirmPassword']
#         voice = request.files['voice']

#         print(email, username, avatarName, relationship,
#               additional, password, confirmPassword, voice)

#         # Save the audio file to a server directory
#         voice_path = f"voices/{username}_{avatarName}_voice.wav"
#         voice.save(voice_path)

#         # Create a new User instance
#         new_user = User(email=email, username=username, avatarName=avatarName,
#                         relationship=relationship, additional=additional, password=password, audio_path=voice_path, messages="")

#         # Add the User to the database and commit the changes
#         db.session.add(new_user)
#         db.session.commit()

#         return jsonify({"responseText": "Success"}), 200
#     except Exception as e:
#         print(e)
#         return jsonify({"responseText": "Something went wrong"}), 500


# @app.route('/getUser', methods=['GET'])
# def getUser():
#     try:
#         userName = request.args.get('userName')
#         user = User.query.filter_by(username=userName).first()
#         return jsonify({
#             "username": user.username,
#             "avatarName": user.avatarName,
#             "relationship": user.relationship,
#             "additional": user.additional,
#             "messages": messages_from_db_form(user.messages)
#         }), 200
#     except Exception as e:
#         print(e)
#         return jsonify({"responseText": "Something went wrong"}), 500


# @app.route('/chatbot', methods=['POST'])
# def chatbot():
#     try:
#         data = request.get_json()
#         message = data["message"]
#         userName = data["userName"]
#         userData = User.query.filter_by(username=userName).first()
#         avatarName = userData.avatarName
#         avatarRelationship = userData.relationship
#         avatarAdditional = userData.additional
#         messages = messages_from_db_form(userData.messages)
#         res_stream = generate_chatbot_response(
#             message,
#             avatarName,
#             avatarRelationship, 
#             avatarAdditional,
#             messages
#         )
#         # voice_path = Path.absolute(User.query.filter_by(username=userName, avatarName=avatarName).first().audio_path)
#         # sr, wav = synthesize(res, voice_path)

#         # wav_io = io.BytesIO()
#         # sf.write(wav_io, wav, sr, format='WAV')
#         # wav_io.seek(0)
        
#         # return jsonify({"responseText": res, 'audio': send_file(wav_io, as_attachment=True, download_name='generated_audio.wav'), "responceTime": responceTime}), 200
#         return Response(handle_text_stream(res_stream), mimetype='text/plain')
#     except Exception as e:
#         print(e)
#         return jsonify({"responseText": "Something went wrong", "responceTime": 0}), 500


# @app.route('/stt', methods=['POST'])
# def stt():
#     try:
#         audioBlob = request.files['audio']
#         text = generate_text_from_speech(audioBlob)
#         return jsonify({'text': text}), 200
#     except Exception as e:
#         print(e)
#         return jsonify({'text': 'Something went wrong'}), 500


# if __name__ == '__main__':
#     db.create_all()
#     app.run(debug=True, port=5000)
