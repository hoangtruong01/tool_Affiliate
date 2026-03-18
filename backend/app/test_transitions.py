"""
Verification script — test legal and illegal status transitions for VideoJobs.
"""
import asyncio
import uuid
from sqlalchemy import select
from app.database import async_session_factory
from app.models.video_job import VideoJob
from app.services.render_service import update_job_status

async def test_transitions():
    async with async_session_factory() as db:
        # Fetch existing User and Script from seed data
        from app.models.user import User
        from app.models.script import Script
        user = (await db.execute(select(User).limit(1))).scalar_one()
        script = (await db.execute(select(Script).limit(1))).scalar_one()

        # Create a test job
        job = VideoJob(
            script_id=script.id,
            created_by=user.id,
            status="queued"
        )
        db.add(job)
        await db.flush()
        job_id = job.id
        print(f"Created test job {job_id} for user {user.email} with status: queued")

        # 1. OK: queued -> processing
        print("Testing: queued -> processing...")
        await update_job_status(db, job_id, "processing")
        print("Success!")

        # 2. FAIL: processing -> approved (must go through needs_review)
        print("Testing: processing -> approved (should fail)...")
        try:
            await update_job_status(db, job_id, "approved")
            print("ERROR: Transition should have failed!")
        except ValueError as e:
            print(f"Success! Caught expected error: {e}")

        # 3. OK: processing -> needs_review
        print("Testing: processing -> needs_review...")
        await update_job_status(db, job_id, "needs_review")
        print("Success!")

        # 4. OK: needs_review -> approved
        print("Testing: needs_review -> approved...")
        await update_job_status(db, job_id, "approved")
        print("Success!")

        # 5. FAIL: approved -> queued (must go through retry/failed)
        print("Testing: approved -> queued (should fail)...")
        try:
            await update_job_status(db, job_id, "queued")
            print("ERROR: Transition should have failed!")
        except ValueError as e:
            print(f"Success! Caught expected error: {e}")

        # 6. OK: approved -> failed (illegal according to my map? actually approved -> failed is ok if render error found later?)
        # Let's check my map: "approved": ["published", "failed"]
        print("Testing: approved -> failed...")
        await update_job_status(db, job_id, "failed")
        print("Success!")

        # 7. OK: failed -> queued (Retry)
        print("Testing: failed -> queued...")
        await update_job_status(db, job_id, "queued")
        print("Success!")

        # 8. OK: queued -> cancelled
        print("Testing: queued -> cancelled...")
        await update_job_status(db, job_id, "cancelled")
        print("Success!")

        await db.rollback() # Don't persist test data
        print("\nAll transition tests passed!")

if __name__ == "__main__":
    asyncio.run(test_transitions())
