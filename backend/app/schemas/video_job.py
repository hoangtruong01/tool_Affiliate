"""
VideoJob schemas — request/response models for render job management.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class JobAssetInput(BaseModel):
    """Asset to include in a video job."""
    asset_id: uuid.UUID
    sequence_order: int = 0
    transform_config: Optional[dict] = None


class VideoJobCreate(BaseModel):
    """Create a new render job."""
    script_id: uuid.UUID
    render_config: Optional[dict] = None
    assets: List[JobAssetInput] = []


class VideoJobPublishUpdate(BaseModel):
    """Update a job with publish metadata and feedback."""
    post_url: Optional[str] = None
    performance_notes: Optional[str] = None
    is_successful: Optional[bool] = None


class VideoJobResponse(BaseModel):
    """Video job data in API responses."""
    id: uuid.UUID
    script_id: uuid.UUID
    created_by: uuid.UUID
    status: str
    render_config: Optional[dict] = None
    output_path: Optional[str] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int
    posted_at: Optional[datetime] = None
    platform: Optional[str] = None
    post_url: Optional[str] = None
    performance_notes: Optional[str] = None
    is_successful: Optional[bool] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoJobListResponse(BaseModel):
    items: List[VideoJobResponse]
    total: int
    page: int
    page_size: int


# ── Approval ───────────────────────────────────────
class ApprovalRequest(BaseModel):
    """Submit an approval decision."""
    decision: str  # "approved" | "rejected" | "revision_requested"
    comment: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    reviewer_id: uuid.UUID
    decision: str
    comment: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
