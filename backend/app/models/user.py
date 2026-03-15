"""
User model — authentication and role-based access control.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Role enum used across the app
UserRole = ENUM("admin", "editor", "reviewer", "viewer", name="user_role", create_type=True)


class User(Base):
    """Application user with role-based access."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        UserRole, nullable=False, default="editor"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    products = relationship("Product", back_populates="creator", lazy="selectin")
    scripts = relationship("Script", back_populates="creator", lazy="selectin")
    assets = relationship("Asset", back_populates="uploader", lazy="selectin")
    video_jobs = relationship("VideoJob", back_populates="creator", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"
