"""
PerformanceMetric schemas — request/response models for performance tracking.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PerformanceMetricCreate(BaseModel):
    """Create a new performance metric entry for a published job."""
    views: Optional[int] = Field(None, ge=0)
    watch_time_seconds: Optional[int] = Field(None, ge=0)
    ctr_estimate: Optional[float] = Field(None, ge=0.0, le=100.0)
    conversions: Optional[int] = Field(None, ge=0)
    operator_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None


class PerformanceMetricUpdate(BaseModel):
    """Update a performance metric entry."""
    views: Optional[int] = Field(None, ge=0)
    watch_time_seconds: Optional[int] = Field(None, ge=0)
    ctr_estimate: Optional[float] = Field(None, ge=0.0, le=100.0)
    conversions: Optional[int] = Field(None, ge=0)
    operator_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class PerformanceMetricResponse(BaseModel):
    """Performance metric data in API responses."""
    id: uuid.UUID
    job_id: uuid.UUID
    views: Optional[int] = None
    watch_time_seconds: Optional[int] = None
    ctr_estimate: Optional[float] = None
    conversions: Optional[int] = None
    operator_rating: Optional[int] = None
    notes: Optional[str] = None
    source: str
    recorded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
