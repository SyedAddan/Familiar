# Familiar

A personalized sentient avatar for self-help.

## Local development

1. Copy `server/.env.example` to `server/.env` and set a unique, random
   `SESSION_SECRET` with at least 32 characters, `TOGETHER_API_KEY`, and (if
   avatar speech is enabled) `GOOGLE_TTS_API_KEY`.
2. Copy `client/.env.example` to `client/.env`.
3. From `server`, install packages with `pip install -r requirements.txt` and
   start the API with `uvicorn app:app --reload --port 5000`.
4. From `client`, install packages with `npm ci` and start the UI with
   `npm start`.

For a production deployment, configure the server environment variables in the
hosting provider. Set `SESSION_COOKIE_SECURE=true`; if the UI and API are on
different sites, also set `SESSION_COOKIE_SAMESITE=none`. Set `CORS_ORIGINS` to
the exact UI origin(s). Do not put provider API keys in the client environment:
Google text-to-speech calls are proxied through the authenticated server.

The SQLite database and `.env` files are local-only and are intentionally
ignored by Git.

## Credential incident follow-up

GitHub Secret Scanning reported exposed Google and OpenAI API keys in repository
history. Revoke and replace those keys with their providers, and replace any
other provider keys that were present in historical environment files. Removing
files from the latest commit does not remove them from Git history; sanitizing
published history requires coordinating a history rewrite with collaborators.
