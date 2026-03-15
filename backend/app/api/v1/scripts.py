"""
Script endpoints — CRUD and AI generation.
"""
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.script import (
    ScriptGenerate,
    ScriptUpdate,
    ScriptResponse,
    ScriptListResponse,
)
from app.services.script_service import get_script, list_scripts
from app.tasks.ai_tasks import generate_script_task

router = APIRouter()


@router.get("/", response_model=ScriptListResponse)
async def list_scripts_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    platform: Optional[str] = None,
):
    """List scripts with filters."""
    items, total = await list_scripts(
        db, page=page, page_size=page_size,
        product_id=product_id, status=status_filter, platform=platform,
    )
    return ScriptListResponse(
        items=[ScriptResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_script_endpoint(
    data: ScriptGenerate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Generate a script via AI (async via Celery)."""
    generate_script_task.delay(
        str(data.product_id),
        str(data.angle_id) if data.angle_id else None,
        str(current_user.id),
        data.tone,
        data.platform,
        data.duration_seconds,
    )
    return {"message": "Script generation queued", "product_id": str(data.product_id)}


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script_endpoint(
    script_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get script detail with captions."""
    script = await get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return ScriptResponse.model_validate(script)


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script_endpoint(
    script_id: uuid.UUID,
    data: ScriptUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Edit a script."""
    script = await get_script(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(script, field, value)

    await db.flush()
    await db.refresh(script)
    return ScriptResponse.model_validate(script)
