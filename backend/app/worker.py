"""
Celery worker entry point.
"""
import os
from celery import Celery
from app.config import settings

# Initialize Celery app
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max for any task
    worker_prefetch_multiplier=1, # Process one task at a time for better resource management
)

# Auto-discover tasks from app/tasks directory
celery_app.autodiscover_tasks(["app.tasks"])

# Define task queues to isolate CPU-intensive renders from I/O-bound AI calls
celery_app.conf.task_routes = {
    "app.tasks.ai_tasks.*": {"queue": "ai_tasks"},
    "app.tasks.render_tasks.*": {"queue": "render_tasks"},
}
