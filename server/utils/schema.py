from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel
from sqlalchemy import Column, String


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
    
class SignUp(BaseModel):
    email: str
    username: str
    avatarName: str
    relationship: str
    additional: str
    password: str
    confirmPassword: str
    
class Login(BaseModel):
    username: str
    password: str 

class GetUser(BaseModel):
    userName: str
    
class Chatbot(BaseModel):
    message: str
    userName: str
    
class ClearHistory(BaseModel):
    userName: str