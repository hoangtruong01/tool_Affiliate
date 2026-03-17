import asyncio
import uuid
import os
import logging
import sys

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from app.database import async_session_factory, engine
from app.services import render_service, asset_service
from app.tasks.render_tasks import render_video_task

async def dry_run_render(job_id_str):
    job_id = uuid.UUID(job_id_str)
    print(f"--- DEBUG: Starting dry run for job {job_id} ---")
    
    async with async_session_factory() as db:
        print("1. Fetching job...")
        job = await render_service.get_video_job(db, job_id)
        if not job:
            print("FAIL: Job not found")
            return
        
        print(f"2. Job status: {job.status}")
        print("3. Updating to 'processing'...")
        await render_service.update_job_status(db, job.id, "processing")
        await db.commit()
        print("4. Commit successful")
        
        # Now we don't actually run FFmpeg here again to save time, 
        # let's just test the final update
        print("5. Testing final update to 'needs_review'...")
        await render_service.update_job_status(
            db, job.id, "needs_review", 
            output_path=f"/app/media/renders/test_{job_id.hex}.mp4",
            duration_seconds=30
        )
        print("6. Calling commit...")
        await db.commit()
        print("7. Final commit successful!")
        
        # Verify
        await db.refresh(job)
        print(f"8. Verified status: {job.status}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_render.py <job_id>")
        sys.exit(1)
    
    asyncio.run(dry_run_render(sys.argv[1]))
    # Dispose pool at the end to be clean
    engine.pool.dispose()
    print("--- DEBUG: Finished ---")
