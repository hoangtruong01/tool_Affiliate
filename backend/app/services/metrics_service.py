"""
Metrics service — CRUD for PerformanceMetric entries.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.performance_metric import PerformanceMetric
from app.schemas.performance_metric import PerformanceMetricCreate, PerformanceMetricUpdate

logger = logging.getLogger(__name__)


async def create_metric(
    db: AsyncSession,
    job_id: uuid.UUID,
    data: PerformanceMetricCreate,
) -> PerformanceMetric:
    """Create a new performance metric snapshot for a job."""
    metric = PerformanceMetric(
        job_id=job_id,
        views=data.views,
        watch_time_seconds=data.watch_time_seconds,
        ctr_estimate=data.ctr_estimate,
        conversions=data.conversions,
        operator_rating=data.operator_rating,
        notes=data.notes,
        source="manual",
        recorded_at=data.recorded_at or datetime.now(timezone.utc),
    )
    db.add(metric)
    await db.flush()
    await db.refresh(metric)
    logger.info(f"Created performance metric {metric.id} for job {job_id}")
    return metric


async def list_metrics(
    db: AsyncSession,
    job_id: uuid.UUID,
) -> list[PerformanceMetric]:
    """List all performance metrics for a job, newest first."""
    result = await db.execute(
        select(PerformanceMetric)
        .where(PerformanceMetric.job_id == job_id)
        .order_by(PerformanceMetric.recorded_at.desc())
    )
    return list(result.scalars().all())


async def get_metric(
    db: AsyncSession,
    metric_id: uuid.UUID,
) -> Optional[PerformanceMetric]:
    """Get a single performance metric by ID."""
    result = await db.execute(
        select(PerformanceMetric).where(PerformanceMetric.id == metric_id)
    )
    return result.scalar_one_or_none()


async def update_metric(
    db: AsyncSession,
    metric_id: uuid.UUID,
    data: PerformanceMetricUpdate,
) -> Optional[PerformanceMetric]:
    """Update a performance metric entry."""
    metric = await get_metric(db, metric_id)
    if not metric:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(metric, field, value)

    await db.flush()
    await db.refresh(metric)
    logger.info(f"Updated performance metric {metric_id}")
    return metric
