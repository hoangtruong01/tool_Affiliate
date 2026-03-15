"""
Product schemas — request/response models for product management.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ── Selling Angle ──────────────────────────────────
class SellingAngleResponse(BaseModel):
    id: uuid.UUID
    angle_type: str
    title: str
    description: str
    score: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Product ────────────────────────────────────────
class ProductCreate(BaseModel):
    """Create a new product."""
    name: str = Field(..., min_length=1, max_length=500)
    source_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    """Update product fields."""
    name: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    """Product data in API responses."""
    id: uuid.UUID
    name: str
    source_url: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: str
    ai_analysis: Optional[dict] = None
    created_by: uuid.UUID
    selling_angles: List[SellingAngleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Paginated product list."""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
