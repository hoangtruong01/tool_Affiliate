"""
Script service — business logic for script & caption management.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.script import Script, Caption

logger = logging.getLogger(__name__)


async def create_script(
    db: AsyncSession,
    product_id: uuid.UUID,
    user_id: uuid.UUID,
    hook: str,
    body: str,
    cta: str,
    tone: str = "casual",
    platform: str = "tiktok",
    duration_seconds: Optional[int] = None,
    angle_id: Optional[uuid.UUID] = None,
) -> Script:
    """Create a new script."""
    script = Script(
        product_id=product_id,
        created_by=user_id,
        hook=hook,
        body=body,
        cta=cta,
        tone=tone,
        platform=platform,
        duration_seconds=duration_seconds,
        angle_id=angle_id,
        status="draft",
    )
    db.add(script)
    await db.flush()
    await db.refresh(script)
    return script


async def get_script(db: AsyncSession, script_id: uuid.UUID) -> Optional[Script]:
    """Get a script by ID with captions."""
    result = await db.execute(
        select(Script)
        .options(
            selectinload(Script.captions),
            selectinload(Script.product)
        )
        .where(Script.id == script_id)
    )
    return result.scalar_one_or_none()


async def list_scripts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    product_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    platform: Optional[str] = None,
) -> tuple[list[Script], int]:
    """List scripts with pagination and filters."""
    query = select(Script).options(selectinload(Script.captions))

    if product_id:
        query = query.where(Script.product_id == product_id)
    if status:
        query = query.where(Script.status == status)
    if platform:
        query = query.where(Script.platform == platform)

    count_query = select(sql_func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Script.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_caption(
    db: AsyncSession,
    script_id: uuid.UUID,
    caption_text: str,
    cta_text: Optional[str] = None,
    hashtags: Optional[list] = None,
    platform: str = "tiktok",
) -> Caption:
    """Create a caption for a script."""
    caption = Caption(
        script_id=script_id,
        caption_text=caption_text,
        cta_text=cta_text,
        hashtags=hashtags,
        platform=platform,
        status="draft",
    )
    db.add(caption)
    await db.flush()
    await db.refresh(caption)
    return caption
