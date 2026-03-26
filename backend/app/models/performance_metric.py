"""
PerformanceMetric model — post-publish performance tracking for video jobs.
Supports manual entry and future API-sync without schema changes.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PerformanceMetric(Base):
    """Performance snapshot for a published video job.
    
    Multiple entries per job are allowed to track metrics over time
    (e.g. day-1 vs day-7 performance).
    """

    __tablename__ = "performance_metrics"
    __table_args__ = (
        CheckConstraint("operator_rating IS NULL OR (operator_rating >= 1 AND operator_rating <= 5)",
                        name="ck_operator_rating_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Core metrics — all nullable for manual/partial entry
    views: Mapped[int | None] = mapped_column(Integer)
    watch_time_seconds: Mapped[int | None] = mapped_column(Integer)
    ctr_estimate: Mapped[float | None] = mapped_column(Float)
    conversions: Mapped[int | None] = mapped_column(Integer)
    operator_rating: Mapped[int | None] = mapped_column(Integer)  # 1-5
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), default="manual")  # "manual" | "api_sync" — for future extensibility

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    job = relationship("VideoJob", back_populates="performance_metrics")

    def __repr__(self) -> str:
        return f"<PerformanceMetric job={self.job_id} views={self.views} rating={self.operator_rating}>"
