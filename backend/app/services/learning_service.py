"""
Learning service — rule-based ranking and analytics from published video performance data.
No ML, embeddings, or complex scoring. Simple aggregation and heuristic-based recommendations.
"""
import logging
from typing import Any

from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.video_job import VideoJob
from app.models.product import Product, SellingAngle
from app.models.script import Script
from app.models.performance_metric import PerformanceMetric

logger = logging.getLogger(__name__)


async def get_learning_insights(db: AsyncSession) -> dict[str, Any]:
    """Generate rule-based learning insights from published video performance data."""

    # ── Top Products ──
    # Rank products by average operator_rating and total views across published jobs
    top_products_q = (
        select(
            Product.id,
            Product.name,
            func.count(VideoJob.id).label("published_count"),
            func.avg(PerformanceMetric.operator_rating).label("avg_rating"),
            func.sum(PerformanceMetric.views).label("total_views"),
        )
        .join(Script, Script.product_id == Product.id)
        .join(VideoJob, VideoJob.script_id == Script.id)
        .outerjoin(PerformanceMetric, PerformanceMetric.job_id == VideoJob.id)
        .where(VideoJob.status == "published")
        .group_by(Product.id, Product.name)
        .order_by(func.avg(PerformanceMetric.operator_rating).desc().nullslast())
        .limit(10)
    )
    top_products_result = await db.execute(top_products_q)
    top_products = [
        {
            "product_id": str(r.id),
            "product_name": r.name,
            "published_count": r.published_count,
            "avg_rating": round(float(r.avg_rating), 1) if r.avg_rating else None,
            "total_views": int(r.total_views) if r.total_views else 0,
        }
        for r in top_products_result.all()
    ]

    # ── Top / Bottom Hooks ──
    # Rank hooks (Script.hook text) by average performance
    hooks_q = (
        select(
            Script.hook,
            Script.id.label("script_id"),
            Product.name.label("product_name"),
            func.avg(PerformanceMetric.operator_rating).label("avg_rating"),
            func.sum(PerformanceMetric.views).label("total_views"),
        )
        .join(VideoJob, VideoJob.script_id == Script.id)
        .join(Product, Script.product_id == Product.id)
        .outerjoin(PerformanceMetric, PerformanceMetric.job_id == VideoJob.id)
        .where(VideoJob.status == "published")
        .group_by(Script.id, Script.hook, Product.name)
        .order_by(func.avg(PerformanceMetric.operator_rating).desc().nullslast())
    )
    hooks_result = await db.execute(hooks_q)
    all_hooks = [
        {
            "script_id": str(r.script_id),
            "hook": r.hook[:100] if r.hook else "",
            "product_name": r.product_name,
            "avg_rating": round(float(r.avg_rating), 1) if r.avg_rating else None,
            "total_views": int(r.total_views) if r.total_views else 0,
        }
        for r in hooks_result.all()
    ]
    top_hooks = [h for h in all_hooks if h["avg_rating"] is not None and h["avg_rating"] >= 3.5][:5]
    weak_hooks = [h for h in all_hooks if h["avg_rating"] is not None and h["avg_rating"] < 3.0][:5]

    # ── Top / Bottom Selling Angles ──
    angles_q = (
        select(
            SellingAngle.id,
            SellingAngle.title,
            SellingAngle.angle_type,
            Product.name.label("product_name"),
            func.count(VideoJob.id).label("job_count"),
            func.avg(PerformanceMetric.operator_rating).label("avg_rating"),
            func.sum(PerformanceMetric.views).label("total_views"),
        )
        .join(Script, Script.angle_id == SellingAngle.id)
        .join(VideoJob, VideoJob.script_id == Script.id)
        .join(Product, SellingAngle.product_id == Product.id)
        .outerjoin(PerformanceMetric, PerformanceMetric.job_id == VideoJob.id)
        .where(VideoJob.status == "published")
        .group_by(SellingAngle.id, SellingAngle.title, SellingAngle.angle_type, Product.name)
        .order_by(func.avg(PerformanceMetric.operator_rating).desc().nullslast())
    )
    angles_result = await db.execute(angles_q)
    all_angles = [
        {
            "angle_id": str(r.id),
            "title": r.title,
            "angle_type": r.angle_type,
            "product_name": r.product_name,
            "job_count": r.job_count,
            "avg_rating": round(float(r.avg_rating), 1) if r.avg_rating else None,
            "total_views": int(r.total_views) if r.total_views else 0,
        }
        for r in angles_result.all()
    ]
    top_angles = [a for a in all_angles if a["avg_rating"] is not None and a["avg_rating"] >= 3.5][:5]
    weak_angles = [a for a in all_angles if a["avg_rating"] is not None and a["avg_rating"] < 3.0][:5]

    # ── Retry Candidates ──
    # Jobs published with poor outcome or low rating that have other angles that haven't been tried
    retry_q = (
        select(
            VideoJob.id.label("job_id"),
            Script.hook,
            Product.name.label("product_name"),
            PerformanceMetric.operator_rating,
            VideoJob.publish_outcome,
        )
        .join(Script, VideoJob.script_id == Script.id)
        .join(Product, Script.product_id == Product.id)
        .outerjoin(PerformanceMetric, PerformanceMetric.job_id == VideoJob.id)
        .where(
            VideoJob.status == "published",
            (PerformanceMetric.operator_rating <= 2) | (VideoJob.publish_outcome == "underperform")
        )
        .order_by(PerformanceMetric.operator_rating.asc().nullslast())
        .limit(10)
    )
    retry_result = await db.execute(retry_q)
    retry_candidates = [
        {
            "job_id": str(r.job_id),
            "hook": r.hook[:80] if r.hook else "",
            "product_name": r.product_name,
            "operator_rating": r.operator_rating,
            "publish_outcome": r.publish_outcome,
            "recommendation": "Try different angle or hook for this product",
        }
        for r in retry_result.all()
    ]

    # ── Drop Candidates ──
    # Products with 3+ published jobs that all have avg rating < 2.5
    drop_q = (
        select(
            Product.id,
            Product.name,
            func.count(VideoJob.id).label("published_count"),
            func.avg(PerformanceMetric.operator_rating).label("avg_rating"),
        )
        .join(Script, Script.product_id == Product.id)
        .join(VideoJob, VideoJob.script_id == Script.id)
        .outerjoin(PerformanceMetric, PerformanceMetric.job_id == VideoJob.id)
        .where(VideoJob.status == "published")
        .group_by(Product.id, Product.name)
        .having(
            and_(
                func.count(VideoJob.id) >= 3,
                func.avg(PerformanceMetric.operator_rating) < 2.5,
            )
        )
        .order_by(func.avg(PerformanceMetric.operator_rating).asc())
        .limit(5)
    )
    drop_result = await db.execute(drop_q)
    drop_candidates = [
        {
            "product_id": str(r.id),
            "product_name": r.name,
            "published_count": r.published_count,
            "avg_rating": round(float(r.avg_rating), 1) if r.avg_rating else None,
            "recommendation": "Consider dropping — consistently underperforming",
        }
        for r in drop_result.all()
    ]

    return {
        "top_products": top_products,
        "top_hooks": top_hooks,
        "weak_hooks": weak_hooks,
        "top_angles": top_angles,
        "weak_angles": weak_angles,
        "retry_candidates": retry_candidates,
        "drop_candidates": drop_candidates,
    }


async def get_reports_data(db: AsyncSession) -> dict[str, Any]:
    """Generate operator-facing report data."""

    # Summary counts
    approved_count = (await db.execute(
        select(func.count()).select_from(VideoJob).where(VideoJob.status == "approved")
    )).scalar() or 0

    published_count = (await db.execute(
        select(func.count()).select_from(VideoJob).where(VideoJob.status == "published")
    )).scalar() or 0

    failed_count = (await db.execute(
        select(func.count()).select_from(VideoJob).where(VideoJob.status == "failed")
    )).scalar() or 0

    # Top performing published videos (by views then rating)
    top_videos_q = (
        select(
            VideoJob.id,
            Script.hook,
            Product.name.label("product_name"),
            VideoJob.post_url,
            VideoJob.posted_at,
            VideoJob.platform,
            VideoJob.publish_outcome,
            PerformanceMetric.views,
            PerformanceMetric.operator_rating,
            PerformanceMetric.conversions,
        )
        .join(Script, VideoJob.script_id == Script.id)
        .join(Product, Script.product_id == Product.id)
        .outerjoin(PerformanceMetric, PerformanceMetric.job_id == VideoJob.id)
        .where(VideoJob.status == "published")
        .order_by(
            PerformanceMetric.views.desc().nullslast(),
            PerformanceMetric.operator_rating.desc().nullslast(),
        )
        .limit(20)
    )
    top_videos_result = await db.execute(top_videos_q)
    top_performing = [
        {
            "job_id": str(r.id),
            "hook": r.hook[:100] if r.hook else "",
            "product_name": r.product_name,
            "post_url": r.post_url,
            "posted_at": r.posted_at.isoformat() if r.posted_at else None,
            "platform": r.platform,
            "publish_outcome": r.publish_outcome,
            "views": r.views,
            "operator_rating": r.operator_rating,
            "conversions": r.conversions,
        }
        for r in top_videos_result.all()
    ]

    # Failed jobs (most recent)
    failed_q = (
        select(
            VideoJob.id,
            Script.hook,
            Product.name.label("product_name"),
            VideoJob.error_message,
            VideoJob.retry_count,
            VideoJob.created_at,
        )
        .join(Script, VideoJob.script_id == Script.id)
        .join(Product, Script.product_id == Product.id)
        .where(VideoJob.status == "failed")
        .order_by(VideoJob.created_at.desc())
        .limit(20)
    )
    failed_result = await db.execute(failed_q)
    failed_jobs = [
        {
            "job_id": str(r.id),
            "hook": r.hook[:80] if r.hook else "",
            "product_name": r.product_name,
            "error_message": r.error_message[:200] if r.error_message else None,
            "retry_count": r.retry_count,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in failed_result.all()
    ]

    # Stuck jobs (processing > 30 min)
    from datetime import datetime, timedelta, timezone
    stuck_threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
    stuck_q = (
        select(
            VideoJob.id,
            VideoJob.started_at,
            VideoJob.status,
        )
        .where(
            VideoJob.status == "processing",
            VideoJob.started_at < stuck_threshold,
        )
        .order_by(VideoJob.started_at.asc())
    )
    stuck_result = await db.execute(stuck_q)
    stuck_jobs = [
        {
            "job_id": str(r.id),
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "status": r.status,
        }
        for r in stuck_result.all()
    ]

    return {
        "summary": {
            "approved_count": approved_count,
            "published_count": published_count,
            "failed_count": failed_count,
        },
        "top_performing": top_performing,
        "failed_jobs": failed_jobs,
        "stuck_jobs": stuck_jobs,
    }
