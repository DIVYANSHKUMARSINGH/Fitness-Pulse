# FitnessPulse API

AI-enhanced fitness tracking backend built with FastAPI, SQLAlchemy (SQLite) and Google Gemini.
Layered architecture (routes -> services -> models), fully mocked AI tests, and GitHub Actions CI.

## Setup
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # set GEMINI_API_KEY
uvicorn app.main:app --reload
```
Docs at http://localhost:8000/docs

## Endpoints (`/api/v1`)
| Method | Path | Description |
|---|---|---|
| GET | /health | Health check |
| POST/GET | /users | Create / list users |
| GET/PUT/DELETE | /users/{id} | User by ID |
| POST/GET | /users/{id}/workouts | Log / list workouts |
| GET/DELETE | /workouts/{id} | Workout by ID |
| GET | /users/{id}/insights | AI coaching tip + stats (404/502/503 on errors) |

## Testing
```bash
pytest --cov=app
```
The Gemini client is injected (`get_ai_client`) and faked in tests; no network or API key is needed.

## Architecture notes
- `app/services/gemini_service.py`: `AIClient` protocol, `GeminiClient` with retry + exponential backoff, pure `compute_stats`/`build_prompt`.
- AI failures map to HTTP 503 (unavailable/unconfigured) and 502 (empty response).
- CI: `.github/workflows/ci.yml` runs tests on Python 3.11/3.12 with a coverage gate.
