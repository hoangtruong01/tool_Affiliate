"""
Caption endpoints — CRUD and AI generation.
"""
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.script import (
    CaptionGenerate,
    CaptionUpdate,
    CaptionResponse,
)
from app.services.caption_service import get_caption, update_caption, list_captions
from app.tasks.ai_tasks import generate_caption_task

router = APIRouter()


@router.get("/", response_model=list[CaptionResponse])
async def list_captions_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    script_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
):
    """List captions."""
    captions = await list_captions(db, script_id=script_id, status=status_filter)
    return [CaptionResponse.model_validate(c) for c in captions]


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_caption_endpoint(
    data: CaptionGenerate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Generate a caption via AI (async via Celery)."""
    generate_caption_task.delay(str(data.script_id), data.platform)
    return {"message": "Caption generation queued", "script_id": str(data.script_id)}


@router.put("/{caption_id}", response_model=CaptionResponse)
async def update_caption_endpoint(
    caption_id: uuid.UUID,
    data: CaptionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Edit a caption."""
    caption = await update_caption(db, caption_id, data)
    if not caption:
        raise HTTPException(status_code=404, detail="Caption not found")
    return CaptionResponse.model_validate(caption)
