"""
Verification script — test legal and illegal status transitions for VideoJobs.

Phase C tests cover:
  - cannot approve an approved job
  - cannot reject a failed job
  - cannot retry an approved job
  - cancel only works for queued/processing
"""
import asyncio
from sqlalchemy import select
from app.database import async_session_factory
from app.models.video_job import VideoJob
from app.services.render_service import update_job_status, cancel_video_job

passed = 0
failed = 0

def ok(msg):
    global passed
    passed += 1
    print(f"  ✓ {msg}")

def fail(msg):
    global failed
    failed += 1
    print(f"  ✗ {msg}")

async def expect_ok(db, job_id, target, label):
    """Expect a transition to succeed."""
    try:
        await update_job_status(db, job_id, target)
        ok(label)
    except ValueError as e:
        fail(f"{label} — unexpected error: {e}")

async def expect_fail(db, job_id, target, label):
    """Expect a transition to raise ValueError."""
    try:
        await update_job_status(db, job_id, target)
        fail(f"{label} — should have raised ValueError!")
    except ValueError:
        ok(label)

def make_job(script_id, user_id, status="queued"):
    return VideoJob(script_id=script_id, created_by=user_id, status=status)


async def test_transitions():
    async with async_session_factory() as db:
        from app.models.user import User
        from app.models.script import Script
        user = (await db.execute(select(User).limit(1))).scalar_one()
        script = (await db.execute(select(Script).limit(1))).scalar_one()
        sid, uid = script.id, user.id

        # ── Happy path: queued → processing → needs_review → approved ──
        print("\n[1] Happy path")
        j1 = make_job(sid, uid)
        db.add(j1); await db.flush()
        await expect_ok(db, j1.id, "processing",    "queued → processing")
        await expect_ok(db, j1.id, "needs_review",  "processing → needs_review")
        await expect_ok(db, j1.id, "approved",       "needs_review → approved")

        # ── Cannot re-approve or go backwards from approved ──
        print("\n[2] Cannot go backwards from approved")
        await expect_fail(db, j1.id, "needs_review", "approved → needs_review")

        # ── Cannot retry an approved job ──
        print("\n[3] Cannot retry approved job")
        await expect_fail(db, j1.id, "queued", "approved → queued")

        # ── Cannot fail an approved job ──
        print("\n[4] Cannot fail approved job")
        await expect_fail(db, j1.id, "failed", "approved → failed")

        # ── Cannot reject a failed job ──
        print("\n[5] Cannot reject a failed job")
        j2 = make_job(sid, uid, status="failed")
        db.add(j2); await db.flush()
        await expect_fail(db, j2.id, "rejected", "failed → rejected")

        # ── Retry works from failed/rejected/cancelled ──
        print("\n[6] Retry from terminal states")
        await expect_ok(db, j2.id, "queued", "failed → queued (retry)")

        j3 = make_job(sid, uid, status="rejected")
        db.add(j3); await db.flush()
        await expect_ok(db, j3.id, "queued", "rejected → queued (retry)")

        j4 = make_job(sid, uid, status="cancelled")
        db.add(j4); await db.flush()
        await expect_ok(db, j4.id, "queued", "cancelled → queued (retry)")

        # ── Cancel only works for queued & processing ──
        print("\n[7] Cancel only from queued/processing")
        j5 = make_job(sid, uid, status="queued")
        db.add(j5); await db.flush()
        try:
            await cancel_video_job(db, j5.id)
            ok("cancel from queued")
        except ValueError:
            fail("cancel from queued — should have succeeded")

        j6 = make_job(sid, uid, status="needs_review")
        db.add(j6); await db.flush()
        try:
            await cancel_video_job(db, j6.id)
            fail("cancel from needs_review — should have raised ValueError")
        except ValueError:
            ok("cancel from needs_review blocked")

        j7 = make_job(sid, uid, status="approved")
        db.add(j7); await db.flush()
        try:
            await cancel_video_job(db, j7.id)
            fail("cancel from approved — should have raised ValueError")
        except ValueError:
            ok("cancel from approved blocked")

        # ── Processing → approved skips needs_review (illegal) ──
        print("\n[8] Cannot skip review")
        j8 = make_job(sid, uid, status="processing")
        db.add(j8); await db.flush()
        await expect_fail(db, j8.id, "approved", "processing → approved")

        await db.rollback()
        print(f"\n{'='*40}")
        print(f"Results: {passed} passed, {failed} failed")
        if failed:
            print("SOME TESTS FAILED!")
        else:
            print("ALL TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_transitions())
