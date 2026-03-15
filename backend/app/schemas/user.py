"""
User schemas — request/response models for auth & user management.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ────────────────────────────────
class UserRegister(BaseModel):
    """Registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserRoleUpdate(BaseModel):
    """Admin: change user role."""
    role: str = Field(..., pattern="^(admin|editor|reviewer|viewer)$")


# ── Response Schemas ───────────────────────────────
class UserResponse(BaseModel):
    """User data returned in API responses."""
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
