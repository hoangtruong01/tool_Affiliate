"""
Script & Caption schemas — request/response models.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ── Script ─────────────────────────────────────────
class ScriptGenerate(BaseModel):
    """Request AI script generation."""
    product_id: uuid.UUID
    angle_id: Optional[uuid.UUID] = None
    tone: str = Field(default="casual", pattern="^(casual|professional|urgent|funny)$")
    platform: str = Field(default="tiktok", pattern="^(tiktok|shopee|instagram|youtube_shorts)$")
    duration_seconds: Optional[int] = Field(default=30, ge=5, le=180)


class ScriptUpdate(BaseModel):
    """Edit a script."""
    hook: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    tone: Optional[str] = None
    platform: Optional[str] = None


class CaptionResponse(BaseModel):
    id: uuid.UUID
    caption_text: str
    cta_text: Optional[str] = None
    hashtags: Optional[list] = None
    platform: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ScriptResponse(BaseModel):
    """Script data in API responses."""
    id: uuid.UUID
    product_id: uuid.UUID
    angle_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    hook: str
    body: str
    cta: str
    tone: str
    platform: str
    duration_seconds: Optional[int] = None
    status: str
    captions: List[CaptionResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScriptListResponse(BaseModel):
    items: List[ScriptResponse]
    total: int
    page: int
    page_size: int


# ── Caption ────────────────────────────────────────
class CaptionGenerate(BaseModel):
    """Request AI caption generation."""
    script_id: uuid.UUID
    platform: str = Field(default="tiktok", pattern="^(tiktok|shopee|instagram|youtube_shorts)$")


class CaptionUpdate(BaseModel):
    caption_text: Optional[str] = None
    cta_text: Optional[str] = None
    hashtags: Optional[list] = None
