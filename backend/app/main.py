"""
AI Video Affiliate Tool — FastAPI Application Entry Point
"""
import os
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import settings
from app.database import engine, Base, get_db
from app.api.v1.router import api_v1_router


# Configure structured logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True
        },
        "app": {"level": "INFO"},
        "sqlalchemy.engine": {"level": "WARNING"},
    }
}
logging.config.dictConfig(LOGGING_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup & shutdown events."""
    # Startup: create tables if they don't exist (dev only; use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered affiliate video generation & management platform",
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for static file access
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

# Include API router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


# Health Check Endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "version": settings.PROJECT_VERSION}


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    """Detailed health check for production monitoring."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unreachable: {str(e)}"
    
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "version": settings.PROJECT_VERSION,
        "database": db_status,
        "media_storage": "accessible" if os.access(settings.MEDIA_DIR, os.W_OK) else "readonly/missing",
    }
