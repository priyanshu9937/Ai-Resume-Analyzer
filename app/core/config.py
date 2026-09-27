from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Resume Analyzer API"
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./resume_analyzer.db"
    upload_dir: Path = Path("./storage/uploads")
    max_upload_size_bytes: int = 5 * 1024 * 1024
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    api_access_token: str | None = None
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def use_async_postgres_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @model_validator(mode="after")
    def validate_access_token(self) -> "Settings":
        if self.environment.lower() == "production" and not self.api_access_token:
            raise ValueError("API_ACCESS_TOKEN must be configured in production")
        if self.api_access_token and len(self.api_access_token) < 32:
            raise ValueError("API_ACCESS_TOKEN must contain at least 32 characters")
        return self

    def ensure_upload_dir(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_upload_dir()
    return settings
