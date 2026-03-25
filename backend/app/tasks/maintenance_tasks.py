import logging
import asyncio
from datetime import datetime, timedelta, timezone

from app.worker import celery_app
from app.database import async_session_factory
from app.services.render_service import update_job_status
from app.models.video_job import VideoJob
from sqlalchemy import select

logger = logging.getLogger(__name__)

def run_async(coro):
    from app.database import engine
    engine.pool.dispose()
    return asyncio.run(coro)

@celery_app.task(name="app.tasks.maintenance_tasks.cleanup_stale_jobs")
def cleanup_stale_jobs():
    """Celery task wrapper for failing stale jobs."""
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
                logger.info("No stale jobs found.")
                return

            for job in stale_jobs:
                logger.warning(f"Failing stale job {job.id} stuck in processing since {job.started_at}")
                try:
                    await update_job_status(
                        db, 
                        job.id, 
                        status="failed", 
                        error_message="System Error: Job exceeded 1-hour processing timeout."
                    )
                except Exception as e:
                    logger.error(f"Failed to cleanly auto-fail job {job.id}: {e}")
            
            await db.commit()
            logger.info(f"Auto-failed {len(stale_jobs)} stale jobs.")

    run_async(_fail_stale_jobs())
