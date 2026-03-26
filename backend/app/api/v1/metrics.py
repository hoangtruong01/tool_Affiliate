"""
Performance Metrics endpoints — CRUD for post-publish performance tracking.
"""
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.performance_metric import (
    PerformanceMetricCreate,
    PerformanceMetricUpdate,
    PerformanceMetricResponse,
)
from app.services.metrics_service import create_metric, list_metrics, get_metric, update_metric
from app.services.render_service import get_video_job

router = APIRouter()


@router.post(
    "/{job_id}/metrics",
    response_model=PerformanceMetricResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_metric_endpoint(
    job_id: uuid.UUID,
    data: PerformanceMetricCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new performance metric entry for a published job."""
    job = await get_video_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "published":
        raise HTTPException(status_code=400, detail="Metrics can only be added to published jobs")

    metric = await create_metric(db, job_id, data)
    await db.commit()
    return PerformanceMetricResponse.model_validate(metric)


@router.get("/{job_id}/metrics", response_model=List[PerformanceMetricResponse])
async def list_metrics_endpoint(
    job_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all performance metrics for a job."""
    job = await get_video_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    metrics = await list_metrics(db, job_id)
    return [PerformanceMetricResponse.model_validate(m) for m in metrics]


@router.put(
    "/{job_id}/metrics/{metric_id}",
    response_model=PerformanceMetricResponse,
)
async def update_metric_endpoint(
    job_id: uuid.UUID,
    metric_id: uuid.UUID,
    data: PerformanceMetricUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update a performance metric entry."""
    metric = await get_metric(db, metric_id)
    if not metric or metric.job_id != job_id:
        raise HTTPException(status_code=404, detail="Metric not found for this job")

    updated = await update_metric(db, metric_id, data)
    await db.commit()
    return PerformanceMetricResponse.model_validate(updated)
