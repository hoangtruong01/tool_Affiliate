"""
Publishing and Distribution stub endpoints.
These endpoints mark readiness for Phase E but do not actually connect to TikTok/Shopee
until explicit integration in future phases.
"""
from fastapi import APIRouter
import uuid

router = APIRouter()

@router.post("/tiktok/{job_id}", tags=["Publishing"])
async def publish_to_tiktok(job_id: uuid.UUID):
    """Stub endpoint for publishing a video to TikTok."""
    return {"status": "success", "message": f"Successfully published job {job_id} to TikTok", "platform": "tiktok", "url": "https://tiktok.com/@stubbed"}

@router.post("/shopee/{job_id}", tags=["Publishing"])
async def upload_to_shopee_video(job_id: uuid.UUID):
    """Stub endpoint for uploading a video to Shopee Video."""
    return {"status": "success", "message": f"Successfully uploaded job {job_id} to Shopee Video", "platform": "shopee", "url": "https://shopee.sg/video/stubbed"}

@router.post("/youtube/{job_id}", tags=["Publishing"])
async def publish_to_youtube_shorts(job_id: uuid.UUID):
    """Stub endpoint for publishing a video to YouTube Shorts."""
    return {"status": "success", "message": f"Successfully published job {job_id} to YouTube Shorts", "platform": "youtube", "url": "https://youtube.com/shorts/stubbed"}
