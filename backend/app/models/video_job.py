"""
VideoJob & VideoJobAsset models — render job orchestration.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

JobStatus = ENUM(
    "queued", "processing", "needs_review", "failed",
    "approved", "rejected", "published", "cancelled",
    name="job_status", create_type=True,
)


class VideoJob(Base):
    """Video render job tracked through the processing pipeline."""

    __tablename__ = "video_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(JobStatus, default="queued")
    render_config: Mapped[dict | None] = mapped_column(JSONB)
    output_path: Mapped[str | None] = mapped_column(String(1024))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Publish metadata (Phase E)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    platform: Mapped[str | None] = mapped_column(String(50))
    post_url: Mapped[str | None] = mapped_column(String(512))
    performance_notes: Mapped[str | None] = mapped_column(Text)
    is_successful: Mapped[bool | None] = mapped_column(Boolean)

    # Phase F — extended publish metadata
    operator_notes: Mapped[str | None] = mapped_column(Text)
    publish_outcome: Mapped[str | None] = mapped_column(String(50))  # success | underperform | viral | removed

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    script = relationship("Script", back_populates="video_jobs")
    creator = relationship("User", back_populates="video_jobs")
    job_assets = relationship(
        "VideoJobAsset", back_populates="job", cascade="all, delete-orphan"
    )
    performance_metrics = relationship(
        "PerformanceMetric", back_populates="job", cascade="all, delete-orphan",
        order_by="PerformanceMetric.recorded_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<VideoJob {self.id} status={self.status}>"


class VideoJobAsset(Base):
    """Many-to-many link between VideoJob and Asset with ordering."""

    __tablename__ = "video_job_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    sequence_order: Mapped[int] = mapped_column(Integer, default=0)
    transform_config: Mapped[dict | None] = mapped_column(JSONB)

    # Relationships
    job = relationship("VideoJob", back_populates="job_assets")
    asset = relationship("Asset", back_populates="video_job_assets")
