"""
Analytics endpoints — dashboard stats.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.script import Script
from app.models.video_job import VideoJob
from app.models.asset import Asset

router = APIRouter()


@router.get("/dashboard")
async def dashboard_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Aggregate dashboard statistics."""
    # Total counts
    products_total = (await db.execute(
        select(func.count()).select_from(Product).where(Product.status != "archived")
    )).scalar() or 0

    scripts_total = (await db.execute(
        select(func.count()).select_from(Script)
    )).scalar() or 0

    jobs_total = (await db.execute(
        select(func.count()).select_from(VideoJob)
    )).scalar() or 0

    assets_total = (await db.execute(
        select(func.count()).select_from(Asset).where(Asset.status == "active")
    )).scalar() or 0

    # Job status breakdown
    job_stats = {}
    for s in ["queued", "processing", "needs_review", "approved", "rejected", "failed", "cancelled", "published"]:
        count = (await db.execute(
            select(func.count()).select_from(VideoJob).where(VideoJob.status == s)
        )).scalar() or 0
        job_stats[s] = count

    # Pending approvals
    pending_scripts = (await db.execute(
        select(func.count()).select_from(Script).where(Script.status == "draft")
    )).scalar() or 0

    pending_jobs = (await db.execute(
        select(func.count()).select_from(VideoJob).where(VideoJob.status == "needs_review")
    )).scalar() or 0

    return {
        "products_total": products_total,
        "scripts_total": scripts_total,
        "jobs_total": jobs_total,
        "assets_total": assets_total,
        "job_status_breakdown": job_stats,
        "pending_approvals": {
            "scripts": pending_scripts,
            "video_jobs": pending_jobs,
        },
        "success_rate": (
            round(job_stats.get("approved", 0) / jobs_total * 100, 1) if jobs_total > 0 else 0
        ),
    }
