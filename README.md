# AI Resume Analyzer API

FastAPI-based AI Resume Analyzer with a responsive browser workspace for resume parsing, document review, ATS scoring, AI-powered analysis, skill-gap detection, and job-description matching.

## Features

- AI-powered resume analysis
- PDF and DOCX resume parsing
- ATS compatibility scoring
- Job-description matching
- Technical skill analysis
- Skill-gap detection
- Keyword analysis
- Resume strengths and weaknesses
- AI-generated improvement recommendations
- Resume analysis regeneration
- Persistent job-match results
- Responsive browser workspace
- FastAPI REST API
- Swagger/OpenAPI documentation
- SQLite support for local development
- PostgreSQL support for production
- Gemini AI integration
- Deterministic local fallback when Gemini is unavailable
- API authentication support
- File validation and upload limits
- Consistent API error responses

## Requirements

- Python 3.12+
- PostgreSQL for production
- SQLite with `aiosqlite` for local development
- Google Gemini API key for AI-powered analysis

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
