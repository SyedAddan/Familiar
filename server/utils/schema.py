from pydantic import BaseModel


class SignUp(BaseModel):
    email: str
    username: str
    avatarName: str
    relationship: str
    gender: str = "neutral"
    additional: str = ""
    password: str
    confirmPassword: str
    
class Login(BaseModel):
    username: str
    password: str

class Chatbot(BaseModel):
    message: str