"""
Product & SellingAngle models — product management and AI analysis.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ProductStatus = ENUM(
    "draft", "analyzed", "active", "archived",
    name="product_status", create_type=True,
)

AngleType = ENUM(
    "pain_point", "benefit", "comparison", "story", "urgency",
    name="angle_type", create_type=True,
)


class Product(Base):
    """Affiliate product with AI analysis data."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    description: Mapped[str | None] = mapped_column(Text)
    raw_scraped_data: Mapped[str | None] = mapped_column(Text)
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB)
    category: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        ProductStatus, nullable=False, default="draft"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator = relationship("User", back_populates="products")
    selling_angles = relationship(
        "SellingAngle", back_populates="product", cascade="all, delete-orphan"
    )
    scripts = relationship("Script", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product {self.name} status={self.status}>"


class SellingAngle(Base):
    """AI-generated selling angle for a product."""

    __tablename__ = "selling_angles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    angle_type: Mapped[str] = mapped_column(AngleType, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    product = relationship("Product", back_populates="selling_angles")
    scripts = relationship("Script", back_populates="angle")

    def __repr__(self) -> str:
        return f"<SellingAngle {self.angle_type}: {self.title[:30]}>"
