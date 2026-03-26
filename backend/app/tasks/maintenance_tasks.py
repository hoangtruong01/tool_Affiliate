import logging
import asyncio
import os
import time as time_mod
from datetime import datetime, timedelta, timezone

from app.worker import celery_app
from app.database import async_session_factory
from app.services.render_service import update_job_status
from app.models.video_job import VideoJob
from app.models.asset import Asset
from app.config import settings
from sqlalchemy import select

logger = logging.getLogger("maintenance")

def run_async(coro):
    from app.database import engine
    engine.pool.dispose()
    return asyncio.run(coro)

@celery_app.task(name="app.tasks.maintenance_tasks.cleanup_stale_jobs")
def cleanup_stale_jobs():
    """Fail jobs stuck in processing for over 1 hour."""
    async def _fail_stale_jobs():
        async with async_session_factory() as db:
            threshold = datetime.now(timezone.utc) - timedelta(hours=1)
            query = select(VideoJob).where(
                VideoJob.status == "processing",
                VideoJob.started_at < threshold
            )
            result = await db.execute(query)
            stale_jobs = result.scalars().all()
            
            if not stale_jobs:
                logger.info("[StaleJobs] No stale jobs found.")
                return

            for job in stale_jobs:
                logger.warning(f"[StaleJobs] Failing job {job.id} stuck since {job.started_at}")
                try:
                    await update_job_status(
                        db, 
                        job.id, 
                        status="failed", 
                        error_message="System Error: Job exceeded 1-hour processing timeout."
                    )
                except Exception as e:
                    logger.error(f"[StaleJobs] Failed to auto-fail job {job.id}: {e}")
            
            await db.commit()
            logger.info(f"[StaleJobs] Auto-failed {len(stale_jobs)} stale jobs.")

    run_async(_fail_stale_jobs())


@celery_app.task(name="app.tasks.maintenance_tasks.cleanup_stale_media")
def cleanup_stale_media():
    """Remove orphaned media files not referenced by any job or asset, older than 7 days."""
    async def _cleanup():
        async with async_session_factory() as db:
            # Get all referenced file paths from jobs and assets
            job_paths_result = await db.execute(
                select(VideoJob.output_path).where(VideoJob.output_path.isnot(None))
            )
            job_paths = {r[0] for r in job_paths_result.all()}
            
            asset_paths_result = await db.execute(
                select(Asset.file_path).where(Asset.file_path.isnot(None))
            )
            asset_paths = {r[0] for r in asset_paths_result.all()}
            
            referenced_paths = job_paths | asset_paths
            
            media_dir = settings.MEDIA_DIR
            if not os.path.exists(media_dir):
                logger.info("[MediaCleanup] Media directory does not exist, skipping.")
                return
            
            cutoff = time_mod.time() - (7 * 24 * 3600)  # 7 days ago
            removed_count = 0
            removed_bytes = 0
            
            for root, dirs, files in os.walk(media_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    # Skip if file is referenced
                    if fpath in referenced_paths:
                        continue
                    # Skip if file is newer than 7 days
                    try:
                        if os.path.getmtime(fpath) > cutoff:
                            continue
                        fsize = os.path.getsize(fpath)
                        os.remove(fpath)
                        removed_count += 1
                        removed_bytes += fsize
                        logger.info(f"[MediaCleanup] Removed orphaned file: {fpath} ({fsize} bytes)")
                    except Exception as e:
                        logger.error(f"[MediaCleanup] Failed to remove {fpath}: {e}")
            
            logger.info(f"[MediaCleanup] Cleanup complete: removed {removed_count} files ({removed_bytes} bytes)")

    run_async(_cleanup())
