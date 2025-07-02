"""
Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.endpoints import health, models, upload, status, download, admin, logs

api_router = APIRouter()

# Include individual routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(download.router, tags=["download"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])