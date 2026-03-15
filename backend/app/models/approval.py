"""
Approval model — content review workflow.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

DecisionType = ENUM(
    "approved", "rejected", "revision_requested",
    name="decision_type", create_type=True,
)


class Approval(Base):
    """Approval decision for scripts, captions, or video jobs."""

    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # "script" | "caption" | "video_job"
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    decision: Mapped[str] = mapped_column(DecisionType, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    reviewer = relationship("User")

    def __repr__(self) -> str:
        return f"<Approval {self.entity_type}:{self.entity_id} → {self.decision}>"
