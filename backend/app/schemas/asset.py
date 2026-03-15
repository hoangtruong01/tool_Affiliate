"""
Asset schemas — request/response models for media management.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class AssetResponse(BaseModel):
    """Asset data in API responses."""
    id: uuid.UUID
    filename: str
    file_path: str
    asset_type: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    metadata_: Optional[dict] = None
    status: str
    uploaded_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    """Paginated asset list."""
    items: List[AssetResponse]
    total: int
    page: int
    page_size: int
