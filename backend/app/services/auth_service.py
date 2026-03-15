"""
Auth service — user registration, login, token management.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserRegister
from app.utils.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)


async def register_user(db: AsyncSession, data: UserRegister, role: str = "editor") -> User:
    """Register a new user with hashed password."""
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    logger.info(f"User registered: {user.email} with role={role}")
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user by email + password. Returns User or None."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def generate_token(user: User) -> str:
    """Generate a JWT access token for the given user."""
    return create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Fetch a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Fetch a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
