"""
Admin endpoints — user management, AI provider config, audit logs.
"""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import require_role
from app.models.user import User
from app.models.ai_provider import AIProviderConfig
from app.models.audit_log import AuditLog
from app.schemas.user import UserResponse, UserRoleUpdate

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin"))],
):
    """List all users (admin only)."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin"))],
):
    """Change a user's role (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.role
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/ai-providers")
async def list_ai_providers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin"))],
):
    """List AI provider configurations."""
    result = await db.execute(select(AIProviderConfig).order_by(AIProviderConfig.provider_name))
    providers = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "provider_name": p.provider_name,
            "is_active": p.is_active,
            "settings": p.settings,
            "created_at": p.created_at.isoformat(),
        }
        for p in providers
    ]


@router.get("/audit-logs")
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin"))],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """View audit logs (admin only)."""
    query = (
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
