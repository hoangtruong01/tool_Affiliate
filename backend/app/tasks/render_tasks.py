"""
Celery tasks for video rendering using FFmpeg.
"""
import uuid
import logging
import os
import asyncio
from typing import List

from app.worker import celery_app
from app.database import async_session_factory
from app.services import render_service, asset_service
from app.utils.ffmpeg import build_slideshow_command, run_ffmpeg, RenderConfig
from app.config import settings

logger = logging.getLogger(__name__)

def run_async(coro):
    """Bridge between sync Celery and async services."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    return loop.run_until_complete(coro)

@celery_app.task(name="app.tasks.render_tasks.render_video_task", bind=True, max_retries=2)
def render_video_task(self, job_id: str):
    """Background task to render video using FFmpeg."""
    async def _task():
        async with async_session_factory() as db:
            job = await render_service.get_video_job(db, uuid.UUID(job_id))
            if not job:
                logger.error(f"Job {job_id} not found")
                return

            await render_service.update_job_status(db, job.id, "processing")
            await db.commit()

            try:
                # Prepare assets
                assets = []
                # job_assets is a list of VideoJobAsset models
                sorted_job_assets = sorted(job.job_assets, key=lambda x: x.sequence_order)
                
                image_paths = []
                audio_path = None
                
                for ja in sorted_job_assets:
                    # Fetch actual asset details
                    asset = await asset_service.get_asset(db, ja.asset_id)
                    if not asset: continue
                    
                    if asset.asset_type == "image":
                        image_paths.append(asset.file_path)
                    elif asset.asset_type == "audio":
                        audio_path = asset.file_path

                # Prepare output path
                output_filename = f"render_{job.id.hex}.mp4"
                output_dir = os.path.join(settings.MEDIA_DIR, "renders")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, output_filename)

                # Build FFmpeg command
                config = RenderConfig(
                    output_path=output_path,
                    duration=job.duration_seconds or 30
                )
                
                # For MVP, we use those images and maybe a hook text overlay
                text_overlay = job.script.hook[:50] if job.script else None
                
                cmd = build_slideshow_command(
                    image_paths=image_paths,
                    audio_path=audio_path,
                    text_overlay=text_overlay,
                    config=config
                )

                # Execute FFmpeg
                success, message = run_ffmpeg(cmd)

                if success:
                    await render_service.update_job_status(
                        db, job.id, "rendered", 
                        output_path=output_path,
                        duration_seconds=config.duration
                    )
                else:
                    await render_service.update_job_status(
                        db, job.id, "failed", 
                        error_message=message
                    )
                
                await db.commit()

            except Exception as e:
                logger.exception(f"Render failed for job {job_id}")
                await render_service.update_job_status(
                    db, job.id, "failed", 
                    error_message=str(e)
                )
                await db.commit()
                self.retry(exc=e, countdown=120)

    run_async(_task())
