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
    "processing": ["needs_review", "failed", "cancelled"],
    "needs_review": ["approved", "rejected", "failed"],
    "approved": ["published"], # Published might be a final state
    "rejected": ["queued"],
    "failed": ["queued"],
    "cancelled": ["queued"],
    "published": [],
}


def validate_status_transition(current: str, target: str):
    """Ensure a status transition is legally allowed (rejects same-state if not explicitly allowed)."""
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
    status: Optional[str | list[str]] = None,
    product_id: Optional[uuid.UUID] = None,
    created_after: Optional[datetime] = None,
    search: Optional[str] = None,
) -> tuple[list[VideoJob], int]:
    """List video jobs with pagination and filters."""
    query = select(VideoJob)
    
    if product_id or search:
        from app.models.script import Script
        query = query.join(Script, VideoJob.script_id == Script.id)

    if status:
        if isinstance(status, list):
            query = query.where(VideoJob.status.in_(status))
        else:
            query = query.where(VideoJob.status == status)
            
    if product_id:
        from app.models.script import Script
        query = query.where(Script.product_id == product_id)
        
    if search:
        from app.models.script import Script
        query = query.where(Script.hook.ilike(f"%{search}%"))
        
    if created_after:
        query = query.where(VideoJob.created_at >= created_after)

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
    """Update a job's status and related fields with validation and retry resets."""
    job = await get_video_job(db, job_id)
    if not job:
        return None

    # Validate transition
    validate_status_transition(job.status, status)

    # If retrying (moving to queued from a terminal state), reset fields
    if status == "queued" and job.status in ("failed", "rejected", "cancelled"):
        job.started_at = None
        job.completed_at = None
        job.error_message = None
        
        if job.output_path and os.path.exists(job.output_path):
            try:
                os.remove(job.output_path)
                logger.info(f"Deleted old output file for job {job_id}: {job.output_path}")
            except Exception as e:
                logger.error(f"Failed to delete old output file {job.output_path}: {e}")
                
        job.output_path = None
        job.retry_count += 1
        logger.info(f"Job {job_id} reset for retry. Count: {job.retry_count}")

    job.status = status

    if status == "processing":
        job.started_at = datetime.now(timezone.utc)
    elif status in ("needs_review", "failed", "cancelled", "approved"):
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
