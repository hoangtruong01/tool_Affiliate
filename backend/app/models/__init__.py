"""
Models package — import all models here so Alembic can discover them.
"""
from app.models.user import User
from app.models.product import Product, SellingAngle
from app.models.script import Script, Caption
from app.models.asset import Asset
from app.models.video_job import VideoJob, VideoJobAsset
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.ai_provider import AIProviderConfig
from app.models.performance_metric import PerformanceMetric

__all__ = [
    "User",
    "Product",
    "SellingAngle",
    "Script",
    "Caption",
    "Asset",
    "VideoJob",
    "VideoJobAsset",
    "Approval",
    "AuditLog",
    "AIProviderConfig",
    "PerformanceMetric",
]
