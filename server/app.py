import asyncio
from html.parser import HTMLParser
import json
import logging
import os
import secrets
import sqlite3
import uuid
from pathlib import Path
from typing import Generator
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request as URLRequest, urlopen

import uvicorn
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from utils.llm import generate_chatbot_response
from utils.message_handler import messages_from_db_form, messages_to_db_form
from utils.security import hash_password, is_password_hash, verify_password
from utils.schema import Chatbot, Login, SignUp


logger = logging.getLogger(__name__)
SERVER_ROOT = Path(__file__).resolve().parent
DB_PATH = SERVER_ROOT / "users.sqlite3"


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    connection = connect_db()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                email VARCHAR(120) NOT NULL UNIQUE,
                username VARCHAR(80) NOT NULL PRIMARY KEY,
                avatarName VARCHAR(80) NOT NULL UNIQUE,
                relationship VARCHAR(1024) NOT NULL,
                gender VARCHAR(8) NOT NULL,
                additional VARCHAR(1024),
                password VARCHAR(255) NOT NULL,
                audio_path VARCHAR(255) NOT NULL,
                messages VARCHAR(10000)
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


initialize_database()

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

def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = connect_db()
    try:
        yield connection
    finally:
        connection.close()


def get_current_user(
    request: Request, db: sqlite3.Connection = Depends(get_db)
) -> sqlite3.Row:
    username = request.session.get("username")
    if not isinstance(username, str):
        raise HTTPException(status_code=401, detail="Authentication required")

    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()
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
def sign_up(
    request_data: SignUp,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
):
    if request_data.password != request_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        db.execute(
            """
            INSERT INTO user (
                email, username, avatarName, relationship, gender, additional,
                password, audio_path, messages
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_data.email,
                request_data.username,
                request_data.avatarName,
                request_data.relationship,
                request_data.gender,
                request_data.additional,
                hash_password(request_data.password),
                "",
                "",
            ),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username already exists") from exc
    except Exception:
        db.rollback()
        logger.exception("Unable to create account")
        raise HTTPException(status_code=500, detail="Unable to create account")

    request.session.clear()
    request.session["username"] = request_data.username
    csrf_token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = csrf_token
    return {"responseText": "Success", "csrfToken": csrf_token}


@app.post("/uploadAudio", dependencies=[Depends(require_csrf_token)])
async def upload_audio(
    audio: UploadFile = File(...),
    user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    content = await audio.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        await audio.close()
        raise HTTPException(status_code=413, detail="Audio upload exceeds 10 MB")

    voices_dir = SERVER_ROOT / "voices"
    voices_dir.mkdir(parents=True, exist_ok=True)
    voice_path = voices_dir / f"{uuid.uuid4().hex}.wav"
    try:
        voice_path.write_bytes(content)
        db.execute(
            "UPDATE user SET audio_path = ? WHERE username = ?",
            (str(voice_path.relative_to(SERVER_ROOT)), user["username"]),
        )
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
def login(
    request_data: Login,
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
):
    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (request_data.username,)
    ).fetchone()
    if user is None or not verify_password(request_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Username or password is incorrect")

    if not is_password_hash(user["password"]):
        db.execute(
            "UPDATE user SET password = ? WHERE username = ?",
            (hash_password(request_data.password), user["username"]),
        )
        db.commit()

    request.session.clear()
    request.session["username"] = user["username"]
    csrf_token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = csrf_token
    return {"responseText": "Success", "csrfToken": csrf_token}


@app.post("/logout", dependencies=[Depends(require_csrf_token)])
def logout(request: Request):
    request.session.clear()
    return {"responseText": "Success"}


@app.get("/getUser")
def get_user(user: sqlite3.Row = Depends(get_current_user)):
    return {
        "username": user["username"],
        "avatarName": user["avatarName"],
        "relationship": user["relationship"],
        "avatarGender": user["gender"],
        "additional": user["additional"],
        "messages": messages_from_db_form(user["messages"]),
        "speechEnabled": bool(
            os.getenv("ELEVENLABS_API_KEY") and os.getenv("ELEVENLABS_VOICE_ID")
        ),
    }


@app.post("/chatbot", dependencies=[Depends(require_csrf_token)])
def chatbot(
    request_data: Chatbot,
    user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    messages = messages_from_db_form(user["messages"])
    try:
        response_text, messages = generate_chatbot_response(
            request_data.message,
            user["avatarName"],
            user["relationship"],
            user["additional"],
            messages,
        )
        db.execute(
            "UPDATE user SET messages = ? WHERE username = ?",
            (messages_to_db_form(messages), user["username"]),
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Unable to generate or save chatbot response")
        raise HTTPException(status_code=502, detail="Unable to generate chatbot response")

    return {"responseText": response_text}


@app.post("/clearHistory", dependencies=[Depends(require_csrf_token)])
def clear_history(
    user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    db.execute("UPDATE user SET messages = '' WHERE username = ?", (user["username"],))
    db.commit()
    return {"responseText": "Success"}


class TalkingHeadSpeechMarkup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.marks: list[tuple[str, int]] = []

    @property
    def text(self) -> str:
        return "".join(self.text_parts)

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "mark":
            mark_name = dict(attrs).get("name")
            if mark_name is not None:
                self.marks.append((mark_name, len(self.text)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.text_parts.append(data)


def elevenlabs_timepoints(
    marks: list[tuple[str, int]], alignment: dict
) -> list[dict[str, str | float]]:
    characters = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    result: list[dict[str, str | float]] = []
    for mark_name, char_index in marks:
        index = min(char_index, len(starts))
        while index < len(characters) and characters[index].isspace():
            index += 1
        time_seconds = starts[index] if index < len(starts) else 0
        result.append({"markName": mark_name, "timeSeconds": time_seconds})
    return result


@app.post(
    "/tts",
    dependencies=[Depends(get_current_user), Depends(require_csrf_token)],
)
async def text_to_speech(request: Request):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        raise HTTPException(status_code=503, detail="Text-to-speech is not configured")

    body = await request.body()
    if len(body) > 64 * 1024:
        raise HTTPException(status_code=413, detail="Text-to-speech request is too large")
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid text-to-speech request") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("input"), dict):
        raise HTTPException(status_code=400, detail="Invalid text-to-speech request")
    ssml = payload["input"].get("ssml")
    if not isinstance(ssml, str) or len(ssml) > 16 * 1024:
        raise HTTPException(status_code=400, detail="Invalid text-to-speech text")
    markup = TalkingHeadSpeechMarkup()
    try:
        markup.feed(ssml)
        markup.close()
    except (ValueError, AssertionError) as exc:
        raise HTTPException(status_code=400, detail="Invalid speech markup") from exc
    text = markup.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Speech text cannot be empty")
    audio_config = payload.get("audioConfig")
    if not isinstance(audio_config, dict):
        audio_config = {}
    speaking_rate = audio_config.get("speakingRate", 1.0)
    try:
        speed = min(1.2, max(0.7, float(speaking_rate)))
    except (TypeError, ValueError):
        speed = 1.0
    voice = payload.get("voice")
    language_code = voice.get("languageCode", "en") if isinstance(voice, dict) else "en"
    if len(text) > 4500:
        raise HTTPException(status_code=413, detail="Speech text is too long")
    request_payload = {
        "text": text,
        "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5"),
        "language_code": language_code.split("-")[0].lower(),
        "voice_settings": {"speed": speed},
    }

    def synthesize():
        upstream_request = URLRequest(
            "https://api.elevenlabs.io/v1/text-to-speech/"
            f"{quote(voice_id, safe='')}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "xi-api-key": api_key,
            },
            method="POST",
        )
        try:
            with urlopen(upstream_request, timeout=30) as upstream_response:
                return upstream_response.status, json.loads(upstream_response.read())
        except HTTPError as exc:
            logger.warning("ElevenLabs request failed with status %s", exc.code)
            return exc.code, {"detail": "Text-to-speech provider rejected the request"}
        except URLError as exc:
            logger.warning("ElevenLabs request failed: %s", exc.reason)
            raise HTTPException(
                status_code=502, detail="Text-to-speech provider is unavailable"
            ) from exc

    status_code, response_data = await asyncio.to_thread(synthesize)
    if status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=response_data.get("detail", "Text-to-speech provider failed"),
        )
    audio_content = response_data.get("audio_base64")
    alignment = response_data.get("alignment")
    if not isinstance(audio_content, str) or not isinstance(alignment, dict):
        logger.error("ElevenLabs returned a response missing audio or alignment")
        raise HTTPException(status_code=502, detail="Invalid speech provider response")
    return {
        "audioContent": audio_content,
        "timepoints": elevenlabs_timepoints(markup.marks, alignment),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
