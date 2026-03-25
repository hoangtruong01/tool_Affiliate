"""
Application configuration via pydantic-settings.
Reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized, typed application settings."""

    # ── Database ──
    POSTGRES_USER: str = "affiliate_user"
    POSTGRES_PASSWORD: str = "changeme_strong_password"
    POSTGRES_DB: str = "affiliate_tool"
    DATABASE_URL: str = "postgresql+asyncpg://affiliate_user:changeme_strong_password@postgres:5432/affiliate_tool"

    # ── Redis ──
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ── Auth ──
    JWT_SECRET_KEY: str = "changeme_jwt_secret_256bit_minimum"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "changeme_admin_password"

    # ── AI Providers ──
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""

    # ── n8n ──
    N8N_WEBHOOK_URL: str = "http://n8n:5678"

    # ── App ──
    APP_ENV: str = "development"
    MOCK_AI_SERVICES: bool = True
    MOCK_RENDER_PROVIDER: bool = True
    BACKEND_URL: str = "http://api:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    MEDIA_DIR: str = "/app/media"
    MAX_UPLOAD_SIZE_MB: int = 100
    FFMPEG_PATH: str = "/usr/bin/ffmpeg"
    FFMPEG_TIMEOUT_SECONDS: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
