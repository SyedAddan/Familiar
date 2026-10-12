import asyncio
import json
import logging
import os
import secrets
import uuid
from pathlib import Path
from typing import Generator
from urllib.error import HTTPError, URLError
from urllib.request import Request as URLRequest, urlopen

import uvicorn
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.sessions import SessionMiddleware

from utils.llm import generate_chatbot_response
from utils.message_handler import messages_from_db_form, messages_to_db_form
from utils.security import hash_password, is_password_hash, verify_password
from utils.schema import Base, Chatbot, Login, SignUp, User


logger = logging.getLogger(__name__)
SERVER_ROOT = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    ENGINE_OPTIONS = (
        {"connect_args": {"check_same_thread": False}}
        if DATABASE_URL.startswith("sqlite")
        else {}
    )
    engine = create_engine(DATABASE_URL, **ENGINE_OPTIONS)
else:
    engine = create_engine(
        URL.create("sqlite", database=str(SERVER_ROOT / "users.sqlite3")),
        connect_args={"check_same_thread": False},
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET or len(SESSION_SECRET) < 32:
    raise RuntimeError("SESSION_SECRET must contain at least 32 characters")

SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower()
if SESSION_COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    raise RuntimeError("SESSION_COOKIE_SAMESITE must be lax, strict, or none")
if SESSION_COOKIE_SAMESITE == "none" and not SESSION_COOKIE_SECURE:
    raise RuntimeError("SESSION_COOKIE_SECURE must be true when SESSION_COOKIE_SAMESITE is none")

origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
if "*" in origins:
    raise RuntimeError("CORS_ORIGINS must list explicit origins, not a wildcard")

app = FastAPI()
app.mount(
    "/avatars",
    StaticFiles(directory=str(SERVER_ROOT / "avatars")),
    name="avatars",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="familiar_session",
    max_age=60 * 60 * 24,
    same_site=SESSION_COOKIE_SAMESITE,
    https_only=SESSION_COOKIE_SECURE,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    username = request.session.get("username")
    if not isinstance(username, str):
        raise HTTPException(status_code=401, detail="Authentication required")

    user = db.query(User).filter_by(username=username).first()
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_csrf_token(
    request: Request,
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    expected_token = request.session.get("csrf_token")
    if (
        not isinstance(expected_token, str)
        or not isinstance(csrf_token, str)
        or not secrets.compare_digest(csrf_token, expected_token)
    ):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


@app.get("/csrf")
def get_csrf_token(request: Request):
    token = request.session.get("csrf_token")
    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return {"csrfToken": token}


@app.post("/signupInputs", dependencies=[Depends(require_csrf_token)])
def sign_up(request_data: SignUp, request: Request, db: Session = Depends(get_db)):
    if request_data.password != request_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = User(
        email=request_data.email,
        username=request_data.username,
        avatarName=request_data.avatarName,
        relationship=request_data.relationship,
        gender=request_data.gender,
        additional=request_data.additional,
        password=hash_password(request_data.password),
        audio_path="",
        messages="",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username already exists") from exc
    except Exception:
        db.rollback()
        logger.exception("Unable to create account")
        raise HTTPException(status_code=500, detail="Unable to create account")

    request.session.clear()
    request.session["username"] = user.username
    csrf_token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = csrf_token
    return {"responseText": "Success", "csrfToken": csrf_token}


@app.post("/uploadAudio", dependencies=[Depends(require_csrf_token)])
async def upload_audio(
    audio: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await audio.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio upload exceeds 10 MB")

    voices_dir = SERVER_ROOT / "voices"
    voices_dir.mkdir(parents=True, exist_ok=True)
    voice_path = voices_dir / f"{uuid.uuid4().hex}.wav"
    try:
        voice_path.write_bytes(content)
        user.audio_path = str(voice_path.relative_to(SERVER_ROOT))
        db.commit()
    except Exception:
        db.rollback()
        voice_path.unlink(missing_ok=True)
        logger.exception("Unable to save uploaded audio")
        raise HTTPException(status_code=500, detail="Unable to save uploaded audio")
    finally:
        await audio.close()

    return {"responseText": "Success"}


@app.post("/loginInputs", dependencies=[Depends(require_csrf_token)])
def login(request_data: Login, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=request_data.username).first()
    if user is None or not verify_password(request_data.password, user.password):
        raise HTTPException(status_code=401, detail="Username or password is incorrect")

    if not is_password_hash(user.password):
        user.password = hash_password(request_data.password)
        db.commit()

    request.session.clear()
    request.session["username"] = user.username
    csrf_token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = csrf_token
    return {"responseText": "Success", "csrfToken": csrf_token}


@app.post("/logout", dependencies=[Depends(require_csrf_token)])
def logout(request: Request):
    request.session.clear()
    return {"responseText": "Success"}


@app.get("/getUser")
def get_user(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "avatarName": user.avatarName,
        "relationship": user.relationship,
        "avatarGender": user.gender,
        "additional": user.additional,
        "messages": messages_from_db_form(user.messages),
    }


@app.post("/chatbot", dependencies=[Depends(require_csrf_token)])
def chatbot(
    request_data: Chatbot,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = messages_from_db_form(user.messages)
    try:
        response_text, messages = generate_chatbot_response(
            request_data.message,
            user.avatarName,
            user.relationship,
            user.additional,
            messages,
        )
        user.messages = messages_to_db_form(messages)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Unable to generate or save chatbot response")
        raise HTTPException(status_code=502, detail="Unable to generate chatbot response")

    return {"responseText": response_text}


@app.post("/clearHistory", dependencies=[Depends(require_csrf_token)])
def clear_history(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user.messages = ""
    db.commit()
    return {"responseText": "Success"}


@app.post(
    "/tts",
    dependencies=[Depends(get_current_user), Depends(require_csrf_token)],
)
async def text_to_speech(request: Request):
    api_key = os.getenv("GOOGLE_TTS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Text-to-speech is not configured")

    body = await request.body()
    if len(body) > 64 * 1024:
        raise HTTPException(status_code=413, detail="Text-to-speech request is too large")
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid text-to-speech request") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid text-to-speech request")

    def synthesize():
        upstream_request = URLRequest(
            "https://texttospeech.googleapis.com/v1/text:synthesize",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
            },
            method="POST",
        )
        try:
            with urlopen(upstream_request, timeout=30) as upstream_response:
                return (
                    upstream_response.status,
                    upstream_response.read(),
                    upstream_response.headers.get_content_type(),
                )
        except HTTPError as exc:
            return exc.code, exc.read(), "application/json"
        except URLError as exc:
            logger.warning("Google text-to-speech request failed: %s", exc.reason)
            raise HTTPException(
                status_code=502, detail="Text-to-speech provider is unavailable"
            ) from exc

    status_code, content, media_type = await asyncio.to_thread(synthesize)
    return Response(content=content, status_code=status_code, media_type=media_type)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
