"""
Synchronous wrapper for async DB sessions in Celery tasks.
"""
import asyncio
import uuid
import logging
from typing import Optional

from app.worker import celery_app
from app.database import async_session_factory
from app.services import ai_service, product_service, script_service

logger = logging.getLogger(__name__)

def run_async(coro):
    """Bridge between sync Celery and async services."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    return loop.run_until_complete(coro)

@celery_app.task(name="app.tasks.ai_tasks.analyze_product_task", bind=True, max_retries=3)
def analyze_product_task(self, product_id: str):
    """Background task to analyze product via AI."""
    async def _task():
        async with async_session_factory() as db:
            product = await product_service.get_product(db, uuid.UUID(product_id))
            if not product:
                logger.error(f"Product {product_id} not found")
                return

            try:
                # Perform AI analysis
                analysis = await ai_service.analyze_product(
                    product_name=product.name,
                    description=product.description or "",
                    source_url=product.source_url
                )
                
                # Save results and create selling angles
                await product_service.save_analysis_results(db, product.id, analysis)
                await db.commit()
                logger.info(f"Analysis completed for product {product_id}")
            except Exception as e:
                logger.error(f"Analysis failed for product {product_id}: {str(e)}")
                self.retry(exc=e, countdown=60)

    run_async(_task())

@celery_app.task(name="app.tasks.ai_tasks.generate_script_task", bind=True, max_retries=3)
def generate_script_task(self, product_id: str, angle_id: Optional[str], user_id: str, tone: str, platform: str, duration: int):
    """Background task to generate script via AI."""
    async def _task():
        async with async_session_factory() as db:
            product = await product_service.get_product(db, uuid.UUID(product_id))
            angle = None
            if angle_id:
                # Need to find the angle if provided
                from app.models.product import SellingAngle
                from sqlalchemy import select
                result = await db.execute(select(SellingAngle).where(SellingAngle.id == uuid.UUID(angle_id)))
                angle = result.scalar_one_or_none()

            try:
                script_data = await ai_service.generate_script(
                    product_name=product.name,
                    description=product.description or "",
                    angle_title=angle.title if angle else "General",
                    angle_description=angle.description if angle else "",
                    tone=tone,
                    platform=platform,
                    duration_seconds=duration
                )
                
                await script_service.create_script(
                    db=db,
                    product_id=product.id,
                    user_id=uuid.UUID(user_id),
                    hook=script_data["hook"],
                    body=script_data["body"],
                    cta=script_data["cta"],
                    tone=tone,
                    platform=platform,
                    duration_seconds=duration,
                    angle_id=angle.id if angle else None
                )
                await db.commit()
            except Exception as e:
                logger.error(f"Script generation failed: {str(e)}")
                self.retry(exc=e, countdown=30)

    run_async(_task())

@celery_app.task(name="app.tasks.ai_tasks.generate_caption_task", bind=True, max_retries=3)
def generate_caption_task(self, script_id: str, platform: str):
    """Background task to generate social media caption via AI."""
    async def _task():
        async with async_session_factory() as db:
            script = await script_service.get_script(db, uuid.UUID(script_id))
            if not script: return

            try:
                caption_data = await ai_service.generate_caption(
                    script_hook=script.hook,
                    script_body=script.body,
                    product_name=script.product.name,
                    platform=platform
                )
                
                await script_service.create_caption(
                    db=db,
                    script_id=script.id,
                    caption_text=caption_data["caption_text"],
                    cta_text=caption_data.get("cta_text"),
                    hashtags=caption_data.get("hashtags"),
                    platform=platform
                )
                await db.commit()
            except Exception as e:
                logger.error(f"Caption generation failed: {str(e)}")
                self.retry(exc=e, countdown=30)

    run_async(_task())
