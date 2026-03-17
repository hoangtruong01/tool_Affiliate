"""
API v1 Router — aggregates all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.products import router as products_router
from app.api.v1.scripts import router as scripts_router
from app.api.v1.captions import router as captions_router
from app.api.v1.assets import router as assets_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router
from app.api.v1.integrations import router as integrations_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(products_router, prefix="/products", tags=["Products"])
api_v1_router.include_router(scripts_router, prefix="/scripts", tags=["Scripts"])
api_v1_router.include_router(captions_router, prefix="/captions", tags=["Captions"])
api_v1_router.include_router(assets_router, prefix="/assets", tags=["Assets"])
api_v1_router.include_router(jobs_router, prefix="/jobs", tags=["Video Jobs"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_v1_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_v1_router.include_router(integrations_router, prefix="/integrations", tags=["Integrations"])

