import logging
import asyncio
from celery import shared_task
from app.worker import celery_app
from app.database import async_session_factory
from sqlalchemy import select
from app.models.product import Product
from app.tasks.ai_tasks import generate_script_task

logger = logging.getLogger(__name__)

def run_async(coro):
    from app.database import engine
    engine.pool.dispose()
    return asyncio.run(coro)

@celery_app.task(name="app.tasks.automation_tasks.daily_content_generation")
def daily_content_generation():
    """
    Lightweight daily automation picked up by Celery Beat.
    Fetches an active product and triggers a script generation task.
    """
    async def _task():
        async with async_session_factory() as db:
            # Pick a random active product
            result = await db.execute(select(Product).where(Product.is_active == True).limit(1))
            product = result.scalar_one_or_none()
            if not product:
                logger.info("No active products found for daily generation.")
                return

            # Note: in a real system we'd assign this to a system user ID
            # For MVP, we'll pick the first admin user
            from app.models.user import User
            user_res = await db.execute(select(User).where(User.role == "admin").limit(1))
            admin = user_res.scalar_one_or_none()
            if not admin:
                logger.info("No admin found. Cannot generate script.")
                return

            logger.info(f"Triggering script generation for product {product.name}")
            generate_script_task.delay(
                str(product.id),
                str(admin.id),
                "casual",
                "tiktok",
                30
            )

    run_async(_task())
