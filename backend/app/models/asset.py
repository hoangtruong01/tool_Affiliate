"""
Asset model — media file management (images, video clips, audio, fonts).
"""
import uuid
from datetime import datetime

from sqlalchemy import String, BigInteger, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

AssetType = ENUM(
    "image", "video_clip", "audio", "font", "template",
    name="asset_type", create_type=True,
)
AssetStatus = ENUM("active", "archived", name="asset_status", create_type=True)


class Asset(Base):
    """Uploaded media asset for video generation."""

    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    asset_type: Mapped[str] = mapped_column(AssetType, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(127))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    status: Mapped[str] = mapped_column(AssetStatus, default="active")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    uploader = relationship("User", back_populates="assets")
    video_job_assets = relationship("VideoJobAsset", back_populates="asset")

    def __repr__(self) -> str:
        return f"<Asset {self.filename} type={self.asset_type}>"
