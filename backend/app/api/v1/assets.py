"""
Asset endpoints — upload and manage media files.
"""
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.asset import AssetResponse, AssetListResponse
from app.services.asset_service import upload_asset, list_assets, delete_asset

router = APIRouter()


@router.get("/", response_model=AssetListResponse)
async def list_assets_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
):
    """List assets with pagination and type filter."""
    items, total = await list_assets(
        db, page=page, page_size=page_size, asset_type=asset_type,
    )
    return AssetListResponse(
        items=[AssetResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/upload", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
    asset_type: Optional[str] = None,
):
    """Upload a media file."""
    try:
        asset = await upload_asset(db, file, current_user.id, asset_type)
        return AssetResponse.model_validate(asset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset_endpoint(
    asset_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Soft-delete an asset."""
    success = await delete_asset(db, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
