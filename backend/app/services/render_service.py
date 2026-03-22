"""
Render service — video job orchestration and FFmpeg processing.
"""
import uuid
import os
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.video_job import VideoJob, VideoJobAsset
from app.models.asset import Asset
from app.schemas.video_job import VideoJobCreate

logger = logging.getLogger(__name__)


ALLOWED_TRANSITIONS = {
    "queued": ["processing", "cancelled", "failed"],
    "processing": ["rendered", "needs_review", "failed", "cancelled"],
    "rendered": ["needs_review", "failed"],
    "needs_review": ["approved", "rejected", "failed"],
    "approved": ["published", "failed"],
    "rejected": ["queued"],  # Only retry/re-queue is allowed
    "failed": ["queued"],    # Only retry/re-queue is allowed
    "cancelled": ["queued"],
    "published": [],
}


def validate_status_transition(current: str, target: str):
    """Ensure a status transition is legally allowed."""
    if current == target:
        return
    allowed = ALLOWED_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise ValueError(f"Invalid transition from {current} to {target}")


async def create_video_job(
    db: AsyncSession,
    data: VideoJobCreate,
    user_id: uuid.UUID,
) -> VideoJob:
    """Create a new video render job and queue it."""
    job = VideoJob(
        script_id=data.script_id,
        created_by=user_id,
        render_config=data.render_config,
        status="queued",
    )
    db.add(job)
    await db.flush()

    # Link assets to job
    for asset_input in data.assets:
        job_asset = VideoJobAsset(
            job_id=job.id,
            asset_id=asset_input.asset_id,
            sequence_order=asset_input.sequence_order,
            transform_config=asset_input.transform_config,
        )
        db.add(job_asset)

    await db.flush()
    await db.refresh(job)
    return job


async def get_video_job(db: AsyncSession, job_id: uuid.UUID) -> Optional[VideoJob]:
    """Get a video job by ID with assets."""
    result = await db.execute(
        select(VideoJob)
        .options(
            selectinload(VideoJob.job_assets),
            selectinload(VideoJob.script)
        )
        .where(VideoJob.id == job_id)
    )
    return result.scalar_one_or_none()


async def list_video_jobs(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
) -> tuple[list[VideoJob], int]:
    """List video jobs with pagination."""
    query = select(VideoJob)

    if status:
        query = query.where(VideoJob.status == status)

    count_query = select(sql_func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(VideoJob.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_job_status(
    db: AsyncSession,
    job_id: uuid.UUID,
    status: str,
    output_path: Optional[str] = None,
    error_message: Optional[str] = None,
    duration_seconds: Optional[int] = None,
) -> Optional[VideoJob]:
    """Update a job's status and related fields with validation."""
    job = await get_video_job(db, job_id)
    if not job:
        return None

    # Validate transition
    validate_status_transition(job.status, status)

    job.status = status

    if status == "processing":
        job.started_at = datetime.now(timezone.utc)
    elif status in ("rendered", "needs_review", "failed", "cancelled"):
        job.completed_at = datetime.now(timezone.utc)

    if output_path:
        job.output_path = output_path
    if error_message:
        job.error_message = error_message
    if duration_seconds:
        job.duration_seconds = duration_seconds

    await db.flush()
    await db.refresh(job)
    return job


async def cancel_video_job(db: AsyncSession, job_id: uuid.UUID) -> Optional[VideoJob]:
    """Cancel a queued or processing job."""
    job = await get_video_job(db, job_id)
    if not job:
        return None

    if job.status not in ("queued", "processing"):
        raise ValueError(f"Cannot cancel job in status: {job.status}")

    return await update_job_status(db, job_id, "cancelled", error_message="Cancelled by user")
