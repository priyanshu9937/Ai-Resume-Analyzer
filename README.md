# AI Resume Analyzer API

FastAPI resume analyzer with a responsive browser workspace for document review, ATS scoring, and job-description matching.

## Requirements

- Python 3.12+
- PostgreSQL for production, or SQLite with `aiosqlite` for local development

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY` in `.env` to enable Gemini analysis. Without a key, the service uses a deterministic local fallback and makes no external LLM call. In development, the API is open on localhost unless `API_ACCESS_TOKEN` is set. Production requires an access token of at least 32 characters; send it from the UI's Access key panel. The browser keeps the token for the current session only.

## Run

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the resume workspace, or `/docs` for the API contract in development.

## Endpoints

- `GET /` serves the browser workspace; `GET /health` checks API health
- `POST /api/v1/resumes/upload` for PDF/DOCX files up to the configured limit; the response includes parser metadata
- `POST /api/v1/analysis/{resume_id}` with optional `regenerate=true`
- `GET /api/v1/analysis/{resume_id}`
- `POST /api/v1/job-match`; each valid match is persisted for later reporting

Resume files receive generated names and are stored outside the public application surface. API responses do not expose extracted resume text, storage paths, credentials, or stack traces. Validation and service failures use a consistent `{ "error": { "code": "...", "message": "..." } }` response.

Uploads are limited by compressed size, DOCX decompressed size, DOCX part count, and PDF page count. Resume APIs accept an optional Bearer token in development and require one when `ENVIRONMENT=production`. Use HTTPS and a private database/object store when deploying beyond localhost; this project does not yet include user accounts or per-user data isolation.

## Tests

```powershell
pytest -q
```
