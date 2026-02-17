# Dubber AI

Backend for AI-powered audio dubbing.

## Stack
- FastAPI
- SQLite
- SQLModel
- Whisper (soon)
- Ollama (soon)
- Piper TTS (soon)

## Features
- Create dubbing jobs
- Persist jobs with SQLite
- API-first architecture

## Run locally

```bash
# 1) start Redis
brew services start redis

# 2) create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# 3) install dependencies
pip install -r requirements.txt

# 4) run API
uvicorn app.main:app --reload

# 5) run worker (new terminal, same venv)
celery -A app.worker.celery_app worker --loglevel=info
```
