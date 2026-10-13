# Familiar

Familiar is an AI companion with a customizable avatar and chat interface. The
web app is built with React and Vite; a FastAPI server handles accounts,
conversation history, and requests to the language-model and text-to-speech
providers.

## Requirements

- Node.js and npm
- Miniconda or Anaconda
- A Groq API key for chat
- An ElevenLabs API key and voice ID for avatar speech

## Run locally

Open two terminals from the repository root.

### 1. Start the API

In the first terminal:

```powershell
conda create -n familiar python=3.12 -y
conda activate familiar
cd server
Copy-Item .env.example .env
```

Edit `server/.env`. Set `SESSION_SECRET` to a newly generated value of at least
32 characters and add a Groq API key. Add an ElevenLabs API key and voice ID
only if you want the avatar to speak. Groq offers a rate-limited developer
tier, and ElevenLabs currently lists a free API allowance; check each provider
for its current limits and availability.

- [Create a Groq API key](https://console.groq.com/keys)
- [Create an ElevenLabs API key](https://elevenlabs.io/app/developers)

Generate a session secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then install and start the server:

```powershell
python -m pip install -r requirements.txt
uvicorn app:app --reload --port 5000
```

The API stores accounts, chat history, and audio paths in the local SQLite file
`server/users.sqlite3`. The file is created automatically when the server
starts. It is not uploaded to an external database service.

### 2. Start the web app

In the second terminal:

```powershell
cd client
npm ci
Copy-Item .env.example .env
npm start
```

Open the local address printed by Vite (normally `http://localhost:5173`).
`client/.env` sets the API address through `VITE_SERVER_URL`; the example
defaults to `http://localhost:5000`.

## Configuration

The server reads its settings from `server/.env`:

| Variable | Purpose |
| --- | --- |
| `SESSION_SECRET` | Signs session cookies; required, at least 32 characters |
| `GROQ_API_KEY` | Authenticates chat requests |
| `GROQ_API_MODEL` | Groq chat model; defaults to `llama-3.3-70b-versatile` |
| `ELEVENLABS_API_KEY` | Enables avatar speech |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice used for generated speech |
| `ELEVENLABS_MODEL_ID` | Speech model; defaults to `eleven_turbo_v2_5` |
| `CORS_ORIGINS` | Allowed web-app origins; defaults include local Vite addresses |
| `SESSION_COOKIE_SECURE` | Enable for HTTPS deployments |
| `SESSION_COOKIE_SAMESITE` | Cookie policy; use `none` only with secure cookies |

For a deployment, configure these values in the hosting provider rather than
committing secrets. Set `CORS_ORIGINS` to the exact frontend origin. If the
frontend and API are on different sites, configure
`SESSION_COOKIE_SAMESITE=none` and `SESSION_COOKIE_SECURE=true`.

## Checks

From `client`:

```powershell
npm run build
npm test
```

From `server`:

```powershell
python -m unittest discover -s tests
```

Keep `.env` files and the local database private; they are intentionally
excluded from Git. The backend uses Python's built-in `sqlite3` module and
does not support external database URLs.

Avatar speech uses ElevenLabs' timestamped speech API. The server translates
its character timings into the marked-word format TalkingHead uses for
animation and lip sync. Without the ElevenLabs settings, chat remains available
and spoken replies are disabled.
