import uvicorn

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Response

from utils.llm import generate_chatbot_response
from utils.schema import Base, User, SignUp, Login, GetUser, Chatbot, ClearHistory
from utils.message_handler import messages_to_db_form, messages_from_db_form


app = FastAPI()
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

# Allowing CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


if __name__ == '__main__':
    engine = create_engine('sqlite:///users.sqlite3')
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    uvicorn.run(app, host="0.0.0.0", port=8000)