import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
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





class SignUp(BaseModel):
    email: str
    username: str
    avatarName: str
    relationship: str
    additional: str
    password: str
    confirmPassword: str

@app.post('/signupInputs', status_code=200)
def signUp(request_data: SignUp, response: Response):
    try:
        email = request_data.email
        username = request_data.username
        avatarName = request_data.avatarName
        relationship = request_data.relationship
        additional = request_data.additional
        password = request_data.password
        confirmPassword = request_data.confirmPassword
        
        app.state.username = username
        app.state.avatarName = avatarName
        
        # Create a new User instance
        new_user = User(email=email, username=username, avatarName=avatarName,
                        relationship=relationship, additional=additional, password=password, audio_path="", messages="")

        # Add the User to the database and commit the changes
        db.add(new_user)
        db.commit()
        response.status_code = 200
        return {"responseText": "Success"}
    except Exception as e:
        response.status_code = 500
        return {"responseText": "Error", "error": e}


    
@app.post('/uploadAudio', status_code=200)
async def uploadAudio(audio: UploadFile = File(...)):
    try:
        username = app.state.username
        avatarName = app.state.avatarName
        
        app.state.username = None
        app.state.avatarName = None
        
        voice_path = f"voices/{username}_{avatarName}_voice.wav"
        with open(voice_path, "wb") as audio_file:
            audio_file.write(await audio.read())
        
        userData = db.query(User).filter_by(username=username).first()
        userData.audio_path = voice_path
        db.commit()
        
        return {"responseText": "Success"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")



class Login(BaseModel):
    username: str
    password: str

@app.post('/loginInputs', status_code=200)
def login(request_data: Login, response: Response):
    try:
        username = request_data.username
        password = request_data.password
        try:
            user = db.query(User).filter_by(username=username).first()
        except:
            response.status_code = 401
            return {"responseText": "Username or password is incorrect"}
        if user.password == password:
            return {"responseText": "Success"}
        else:
            response.status_code = 401
            return {"responseText": "Username or password is incorrect1"}
    except Exception as e:
        print(e)
        response.status_code = 500
        return {"responseText": "Something went wrong"}



class GetUser(BaseModel):
    userName: str

@app.post('/getUser', status_code=200)
async def getUser(request_data: GetUser, response: Response):
    try:
        userName = request_data.userName
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
        response.status_code = 500
        return {"responseText": "Something went wrong", "error": e}



class Chatbot(BaseModel):
    message: str
    userName: str

@app.post('/chatbot', status_code=200)
async def chatbot(request_data: Chatbot, response: Response):
    try:
        userName = request_data.userName
        message = request_data.message
        userData = db.query(User).filter_by(username=userName).first()
        avatarName = userData.avatarName
        avatarRelationship = userData.relationship
        avatarAdditional = userData.additional
        messages = messages_from_db_form(userData.messages)
        response, messages = generate_chatbot_response(
            message,
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
        response.status_code = 500
        return {"responseText": "Something went wrong", "error": e}



class ClearHistory(BaseModel):
    userName: str

@app.post('/clearHistory', status_code=200)
async def clearhistory(request_data: ClearHistory, response: Response):
    try:
        userName = request_data.userName
        userData = db.query(User).filter_by(username=userName).first()
        userData.messages = ""
        db.commit()
        
        return {"responseText": "Success"}
    except Exception as e:
        print(e)
        response.status_code = 500
        return {"responseText": "Something went wrong", "error": e}

# @app.post('/stt', status_code=200)
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
