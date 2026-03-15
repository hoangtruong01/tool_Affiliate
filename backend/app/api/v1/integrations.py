from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid

from app.api import deps
from app.services.platform_service import platform_service
from app.services.render_service import render_service
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/publish/tiktok/{job_id}", response_model=Dict[str, Any])
async def publish_tiktok(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Publish a rendered video to TikTok.
    """
    job = await render_service.get_video_job(db, job_id)
    if not job or job.status != 'rendered':
        raise HTTPException(status_code=400, detail="Video job not ready or not found")
    
    # In real app, we'd fetch the caption from script.captions
    caption = job.script.captions[0].caption_text if job.script and job.script.captions else "Check this out!"
    hashtags = job.script.captions[0].hashtags if job.script and job.script.captions else "#affiliate"

    result = await platform_service.publish_to_tiktok(
        video_path=job.output_path,
        caption=caption,
        hashtags=hashtags
    )
    return result

@router.post("/publish/shopee/{job_id}", response_model=Dict[str, Any])
async def publish_shopee(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_user)
):
    """
    Publish a rendered video to Shopee.
    """
    job = await render_service.get_video_job(db, job_id)
    if not job or job.status != 'rendered':
        raise HTTPException(status_code=400, detail="Video job not ready or not found")
    
    result = await platform_service.publish_to_shopee(
        video_path=job.output_path,
        product_id=str(job.product_id),
        caption="Review sản phẩm cực xịn!"
    )
    return result
