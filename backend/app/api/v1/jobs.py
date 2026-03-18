"""
Video Job endpoints — create, list, retry, approve/reject.
"""
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.video_job import (
    VideoJobCreate,
    VideoJobResponse,
    VideoJobListResponse,
    ApprovalRequest,
)
from app.services.render_service import (
    create_video_job,
    get_video_job,
    list_video_jobs,
)
from app.services.approval_service import create_approval
from app.tasks.render_tasks import render_video_task

router = APIRouter()


@router.get("/", response_model=VideoJobListResponse)
async def list_jobs_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List video jobs with pagination."""
    items, total = await list_video_jobs(
        db, page=page, page_size=page_size, status=status_filter,
    )
    return VideoJobListResponse(
        items=[VideoJobResponse.model_validate(j) for j in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=VideoJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    data: VideoJobCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new render job and queue it."""
    job = await create_video_job(db, data, current_user.id)

    # Queue the render task
    render_video_task.delay(str(job.id))

    return VideoJobResponse.model_validate(job)


@router.get("/{job_id}", response_model=VideoJobResponse)
async def get_job_endpoint(
    job_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get video job detail."""
    job = await get_video_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return VideoJobResponse.model_validate(job)


@router.post("/{job_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_job_endpoint(
    job_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Retry a failed or rejected render job."""
    from app.services.render_service import update_job_status
    
    try:
        job = await update_job_status(db, job_id, "queued")
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job.retry_count += 1
        job.error_message = None
        await db.flush()

        render_video_task.delay(str(job.id))
        return {"message": "Job retry queued", "job_id": str(job.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_job_endpoint(
    job_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin", "reviewer"))],
):
    """Cancel a queued or processing job."""
    from app.services.render_service import cancel_video_job as svc_cancel_job
    
    try:
        job = await svc_cancel_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"message": "Job cancelled", "job_id": str(job.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/approve")
async def approve_job_endpoint(
    job_id: uuid.UUID,
    data: ApprovalRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin", "reviewer"))],
):
    """Approve or reject a rendered video."""
    try:
        approval = await create_approval(
            db, "video_job", job_id, current_user.id, data.decision, data.comment
        )
        return {"message": f"Job {approval.decision}", "approval_id": str(approval.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
