from contextlib import asynccontextmanager
import secrets
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import analysis, health, job_match, resumes
from app.core.config import get_settings
from app.core.errors import AppError
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


settings = get_settings()
production = settings.environment.lower() == "production"
web_directory = Path(__file__).resolve().parent / "web"
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if production else "/docs",
    redoc_url=None if production else "/redoc",
    openapi_url=None if production else "/openapi.json",
)


@app.middleware("http")
async def protect_api(request: Request, call_next):
    token = settings.api_access_token
    if token and request.url.path.startswith("/api/v1/"):
        provided_token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if not secrets.compare_digest(provided_token, token):
            response = JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
                content={"error": {"code": "unauthorized", "message": "A valid API access token is required"}},
            )
        else:
            response = await call_next(request)
    else:
        response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}})


app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(health.router)
app.include_router(resumes.router)
app.include_router(analysis.router)
app.include_router(job_match.router)
app.mount("/", StaticFiles(directory=web_directory, html=True), name="frontend")
