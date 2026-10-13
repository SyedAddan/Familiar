import os
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SESSION_SECRET", "test-session-secret-at-least-32-chars")

from fastapi.testclient import TestClient

import app as api


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_path_patch = patch.object(api, "DB_PATH", self.root / "users.sqlite3")
        self.server_root_patch = patch.object(api, "SERVER_ROOT", self.root)
        self.db_path_patch.start()
        self.server_root_patch.start()
        api.initialize_database()
        self.client = TestClient(api.app)
        response = self.client.get("/csrf")
        self.assertEqual(response.status_code, 200)
        self.csrf_token = response.json()["csrfToken"]

    def tearDown(self):
        self.client.close()
        self.db_path_patch.stop()
        self.server_root_patch.stop()
        self.temp_dir.cleanup()

    def headers(self):
        return {"X-CSRF-Token": self.csrf_token}

    def signup(self, **overrides):
        payload = {
            "email": "person@example.com",
            "username": "person",
            "avatarName": "Alex",
            "relationship": "supportive friend",
            "gender": "neutral",
            "additional": "",
            "password": "correct horse battery staple",
            "confirmPassword": "correct horse battery staple",
        }
        payload.update(overrides)
        response = self.client.post(
            "/signupInputs", json=payload, headers=self.headers()
        )
        if response.status_code == 200:
            self.csrf_token = response.json()["csrfToken"]
        return response

    def test_signup_creates_sqlite_account_and_authenticated_session(self):
        response = self.signup()

        self.assertEqual(response.status_code, 200)
        self.assertTrue((self.root / "users.sqlite3").is_file())
        user_response = self.client.get("/getUser")
        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(user_response.json()["username"], "person")
        self.assertEqual(user_response.json()["messages"], [])

        with closing(sqlite3.connect(self.root / "users.sqlite3")) as connection:
            stored_password = connection.execute(
                "SELECT password FROM user WHERE username = ?", ("person",)
            ).fetchone()[0]
        self.assertTrue(api.is_password_hash(stored_password))

    def test_signup_rejects_duplicate_email_and_password_mismatch(self):
        self.assertEqual(self.signup().status_code, 200)
        duplicate_email = self.signup(
            username="another", avatarName="Taylor", email="person@example.com"
        )
        self.assertEqual(duplicate_email.status_code, 409)
        mismatch = self.signup(confirmPassword="different")
        self.assertEqual(mismatch.status_code, 400)

    def test_login_verifies_password_and_upgrades_legacy_password(self):
        with closing(sqlite3.connect(self.root / "users.sqlite3")) as connection:
            connection.execute(
                """
                INSERT INTO user (
                    email, username, avatarName, relationship, gender,
                    additional, password, audio_path, messages
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "legacy@example.com",
                    "legacy",
                    "Legacy",
                    "friend",
                    "neutral",
                    "",
                    "legacy-password",
                    "",
                    "",
                ),
            )
            connection.commit()

        bad_login = self.client.post(
            "/loginInputs",
            json={"username": "legacy", "password": "wrong"},
            headers=self.headers(),
        )
        self.assertEqual(bad_login.status_code, 401)
        login_response = self.client.post(
            "/loginInputs",
            json={"username": "legacy", "password": "legacy-password"},
            headers=self.headers(),
        )
        self.assertEqual(login_response.status_code, 200)
        self.csrf_token = login_response.json()["csrfToken"]
        self.assertEqual(self.client.get("/getUser").status_code, 200)

        with closing(sqlite3.connect(self.root / "users.sqlite3")) as connection:
            upgraded_password = connection.execute(
                "SELECT password FROM user WHERE username = ?", ("legacy",)
            ).fetchone()[0]
        self.assertTrue(api.is_password_hash(upgraded_password))

    def test_chat_history_is_saved_and_can_be_cleared(self):
        self.assertEqual(self.signup().status_code, 200)
        with patch.object(
            api,
            "generate_chatbot_response",
            return_value=(
                "Hello!",
                [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello!"},
                ],
            ),
        ):
            chat_response = self.client.post(
                "/chatbot", json={"message": "Hi"}, headers=self.headers()
            )
        self.assertEqual(chat_response.status_code, 200)
        self.assertEqual(chat_response.json()["responseText"], "Hello!")
        self.assertEqual(
            len(self.client.get("/getUser").json()["messages"]), 2
        )

        clear_response = self.client.post("/clearHistory", headers=self.headers())
        self.assertEqual(clear_response.status_code, 200)
        self.assertEqual(self.client.get("/getUser").json()["messages"], [])

    def test_provider_failure_is_reported_without_losing_session(self):
        self.assertEqual(self.signup().status_code, 200)
        with patch.object(
            api, "generate_chatbot_response", side_effect=RuntimeError("provider down")
        ):
            response = self.client.post(
                "/chatbot", json={"message": "Hi"}, headers=self.headers()
            )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(self.client.get("/getUser").status_code, 200)

    def test_audio_upload_saves_file_and_database_path(self):
        self.assertEqual(self.signup().status_code, 200)
        response = self.client.post(
            "/uploadAudio",
            files={"audio": ("voice.wav", b"audio-data", "audio/wav")},
            headers=self.headers(),
        )
        self.assertEqual(response.status_code, 200)

        with closing(sqlite3.connect(self.root / "users.sqlite3")) as connection:
            audio_path = connection.execute(
                "SELECT audio_path FROM user WHERE username = ?", ("person",)
            ).fetchone()[0]
        saved_audio = self.root / audio_path
        self.assertTrue(saved_audio.is_file())
        self.assertEqual(saved_audio.read_bytes(), b"audio-data")

    def test_audio_upload_rejects_files_over_10_mb(self):
        self.assertEqual(self.signup().status_code, 200)
        response = self.client.post(
            "/uploadAudio",
            files={
                "audio": (
                    "oversized.wav",
                    b"x" * (10 * 1024 * 1024 + 1),
                    "audio/wav",
                )
            },
            headers=self.headers(),
        )
        self.assertEqual(response.status_code, 413)

        with closing(sqlite3.connect(self.root / "users.sqlite3")) as connection:
            audio_path = connection.execute(
                "SELECT audio_path FROM user WHERE username = ?", ("person",)
            ).fetchone()[0]
        self.assertEqual(audio_path, "")

    def test_csrf_auth_logout_and_unconfigured_tts(self):
        self.assertEqual(self.client.get("/getUser").status_code, 401)
        self.assertEqual(
            self.client.post("/logout", headers={"X-CSRF-Token": "bad"}).status_code,
            403,
        )
        self.assertEqual(self.signup().status_code, 200)
        with patch.dict(
            os.environ,
            {"ELEVENLABS_API_KEY": "", "ELEVENLABS_VOICE_ID": ""},
        ):
            tts_response = self.client.post(
                "/tts",
                json={},
                headers=self.headers(),
            )
        self.assertEqual(tts_response.status_code, 503)
        logout_response = self.client.post("/logout", headers=self.headers())
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(self.client.get("/getUser").status_code, 401)

    def test_elevenlabs_alignment_is_converted_to_talkinghead_markers(self):
        alignment = {
            "characters": list("Hello there"),
            "character_start_times_seconds": [
                0.0, 0.08, 0.16, 0.24, 0.32, 0.4,
                0.45, 0.5, 0.58, 0.66, 0.74,
            ],
        }
        self.assertEqual(
            api.elevenlabs_timepoints([("1", 6)], alignment),
            [{"markName": "1", "timeSeconds": 0.45}],
        )

    def test_tts_adapts_marked_ssml_and_timestamps_for_talkinghead(self):
        class FakeResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(
                    {
                        "audio_base64": "encoded-audio",
                        "alignment": {
                            "characters": list("Hello there"),
                            "character_start_times_seconds": [
                                0.0, 0.08, 0.16, 0.24, 0.32, 0.4,
                                0.45, 0.5, 0.58, 0.66, 0.74,
                            ],
                        },
                    }
                ).encode()

        self.assertEqual(self.signup().status_code, 200)
        payload = {
            "input": {"ssml": "<speak>Hello <mark name='1'/>there</speak>"},
            "voice": {"languageCode": "en-US", "name": "unused-provider-voice"},
            "audioConfig": {"speakingRate": 1.0},
        }
        with (
            patch.dict(
                os.environ,
                {
                    "ELEVENLABS_API_KEY": "test-key",
                    "ELEVENLABS_VOICE_ID": "test-voice",
                },
            ),
            patch.object(api, "urlopen", return_value=FakeResponse()) as mocked_urlopen,
        ):
            response = self.client.post(
                "/tts", json=payload, headers=self.headers()
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "audioContent": "encoded-audio",
                "timepoints": [{"markName": "1", "timeSeconds": 0.45}],
            },
        )
        request = mocked_urlopen.call_args.args[0]
        self.assertTrue(request.full_url.startswith("https://api.elevenlabs.io/"))
        self.assertEqual(json.loads(request.data)["text"], "Hello there")


if __name__ == "__main__":
    unittest.main()
