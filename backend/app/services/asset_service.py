"""
Asset service — media file upload and management.
"""
import uuid
import os
import logging
import io
from typing import Optional
from datetime import datetime

from fastapi import UploadFile
from PIL import Image
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.asset import Asset

logger = logging.getLogger(__name__)

# Allowed MIME types per asset type
ALLOWED_MIMES = {
    "image": ["image/jpeg", "image/png", "image/webp", "image/gif"],
    "video_clip": ["video/mp4", "video/webm", "video/quicktime"],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3"],
    "font": ["font/ttf", "font/otf", "application/x-font-ttf"],
    "template": ["application/json"],
}


def detect_asset_type(mime_type: str) -> str:
    """Detect asset type from MIME type."""
    for asset_type, mimes in ALLOWED_MIMES.items():
        if mime_type in mimes:
            return asset_type
    return "image"  # default


async def upload_asset(
    db: AsyncSession,
    file: UploadFile,
    user_id: uuid.UUID,
    asset_type: Optional[str] = None,
) -> Asset:
    """Save an uploaded file and create an asset record."""
    # Determine asset type from MIME if not specified
    mime_type = file.content_type or "application/octet-stream"
    if not asset_type:
        asset_type = detect_asset_type(mime_type)

    # Generate unique filename
    ext = os.path.splitext(file.filename or "file")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(settings.MEDIA_DIR, "uploads", asset_type)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)

    # Write file
    content = await file.read()
    
    # Validate image integrity if it's an image
    if asset_type == "image":
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
            logger.info(f"Image validation passed for {file.filename}")
        except Exception as e:
            logger.error(f"Image validation failed for {file.filename}: {str(e)}")
            raise ValueError(f"Invalid or corrupt image file: {str(e)}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Create DB record
    asset = Asset(
        uploaded_by=user_id,
        filename=file.filename or unique_name,
        file_path=file_path,
        asset_type=asset_type,
        mime_type=mime_type,
        file_size=len(content),
        status="active",
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)

    logger.info(f"Asset uploaded: {asset.filename} ({asset.file_size} bytes)")
    return asset


async def list_assets(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    asset_type: Optional[str] = None,
    status: str = "active",
) -> tuple[list[Asset], int]:
    """List assets with pagination and filters."""
    query = select(Asset).where(Asset.status == status)

    if asset_type:
        query = query.where(Asset.asset_type == asset_type)

    count_query = select(sql_func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Asset.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_asset(db: AsyncSession, asset_id: uuid.UUID) -> Optional[Asset]:
    """Get an asset by ID."""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    return result.scalar_one_or_none()


async def delete_asset(db: AsyncSession, asset_id: uuid.UUID) -> bool:
    """Soft-delete an asset."""
    asset = await get_asset(db, asset_id)
    if not asset:
        return False
    asset.status = "archived"
    await db.flush()
    return True
