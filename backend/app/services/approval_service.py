"""
Approval service — content review workflow logic.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.script import Script, Caption
from app.models.video_job import VideoJob

logger = logging.getLogger(__name__)

# Maps entity_type to (Model, status_field_mapping)
ENTITY_MAP = {
    "script": Script,
    "caption": Caption,
    "video_job": VideoJob,
}

DECISION_TO_STATUS = {
    "approved": "approved",
    "rejected": "rejected",
    "revision_requested": "draft",
}


async def create_approval(
    db: AsyncSession,
    entity_type: str,
    entity_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    decision: str,
    comment: Optional[str] = None,
) -> Approval:
    """Create an approval decision and update the entity's status with normalization."""
    from app.services import render_service  # Lazy import to avoid circularity if any

    # Normalize decision
    decision = decision.lower()
    if decision == "approve": decision = "approved"
    if decision == "reject": decision = "rejected"

    if entity_type not in ENTITY_MAP:
        raise ValueError(f"Invalid entity_type: {entity_type}")

    # Update entity status
    if entity_type == "video_job":
        new_status = DECISION_TO_STATUS.get(decision, decision)
        await render_service.update_job_status(db, entity_id, new_status)
    else:
        model = ENTITY_MAP[entity_type]
        result = await db.execute(select(model).where(model.id == entity_id))
        entity = result.scalar_one_or_none()
        if not entity:
            raise ValueError(f"{entity_type} {entity_id} not found")
        
        new_status = DECISION_TO_STATUS.get(decision, decision)
        entity.status = new_status

    # Create approval record
    approval = Approval(
        entity_type=entity_type,
        entity_id=entity_id,
        reviewer_id=reviewer_id,
        decision=decision,
        comment=comment,
        decided_at=datetime.now(timezone.utc),
    )
    db.add(approval)
    await db.flush()
    await db.refresh(approval)

    logger.info(f"Approval created: {entity_type}:{entity_id} → {decision}")
    return approval


async def list_approvals(
    db: AsyncSession,
    entity_type: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
) -> list[Approval]:
    """List approval records."""
    query = select(Approval).order_by(Approval.created_at.desc())

    if entity_type:
        query = query.where(Approval.entity_type == entity_type)
    if entity_id:
        query = query.where(Approval.entity_id == entity_id)

    result = await db.execute(query)
    return list(result.scalars().all())
