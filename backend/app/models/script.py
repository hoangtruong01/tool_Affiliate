"""
Script & Caption models — AI-generated video scripts and social captions.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ScriptStatus = ENUM("draft", "approved", "rejected", name="script_status", create_type=True)
CaptionStatus = ENUM("draft", "approved", "rejected", name="caption_status", create_type=True)
ToneType = ENUM("casual", "professional", "urgent", "funny", name="tone_type", create_type=True)
PlatformType = ENUM(
    "tiktok", "shopee", "instagram", "youtube_shorts",
    name="platform_type", create_type=True,
)


class Script(Base):
    """AI-generated video script with hook, body, CTA structure."""

    __tablename__ = "scripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    angle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("selling_angles.id", ondelete="SET NULL")
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    hook: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(ToneType, default="casual")
    platform: Mapped[str] = mapped_column(PlatformType, default="tiktok")
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(ScriptStatus, default="draft")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    product = relationship("Product", back_populates="scripts")
    angle = relationship("SellingAngle", back_populates="scripts")
    creator = relationship("User", back_populates="scripts")
    captions = relationship("Caption", back_populates="script", cascade="all, delete-orphan")
    video_jobs = relationship("VideoJob", back_populates="script")

    def __repr__(self) -> str:
        return f"<Script {self.id} platform={self.platform} status={self.status}>"


class Caption(Base):
    """AI-generated social media caption with hashtags."""

    __tablename__ = "captions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False
    )
    caption_text: Mapped[str] = mapped_column(Text, nullable=False)
    cta_text: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[dict | None] = mapped_column(JSONB)  # ["#tag1", "#tag2"]
    platform: Mapped[str] = mapped_column(PlatformType, default="tiktok")
    status: Mapped[str] = mapped_column(CaptionStatus, default="draft")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    script = relationship("Script", back_populates="captions")

    def __repr__(self) -> str:
        return f"<Caption {self.id} platform={self.platform}>"
