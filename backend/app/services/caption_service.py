"""
Caption service — business logic for caption management.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.script import Caption
from app.schemas.script import CaptionUpdate

logger = logging.getLogger(__name__)


async def get_caption(db: AsyncSession, caption_id: uuid.UUID) -> Optional[Caption]:
    """Get a caption by ID."""
    result = await db.execute(select(Caption).where(Caption.id == caption_id))
    return result.scalar_one_or_none()


async def update_caption(
    db: AsyncSession, caption_id: uuid.UUID, data: CaptionUpdate
) -> Optional[Caption]:
    """Update a caption."""
    caption = await get_caption(db, caption_id)
    if not caption:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(caption, field, value)

    await db.flush()
    await db.refresh(caption)
    return caption


async def list_captions(
    db: AsyncSession,
    script_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
) -> list[Caption]:
    """List captions with optional filters."""
    query = select(Caption)

    if script_id:
        query = query.where(Caption.script_id == script_id)
    if status:
        query = query.where(Caption.status == status)

    query = query.order_by(Caption.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
