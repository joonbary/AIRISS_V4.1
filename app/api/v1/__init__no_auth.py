"""
API v1 Router Configuration - No Authentication Version
"""

from fastapi import APIRouter

# Import routers
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.download import router as download_router
from app.api.v1.endpoints.employee import router as employee_router
from app.api.v1.endpoints.files_no_auth import router as files_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.search import router as search_router
from app.api.v1.endpoints.status import router as status_router
from app.api.v1.endpoints.upload import router as upload_router
from app.api.v1.endpoints.websocket import router as websocket_router

# Create main router
api_router = APIRouter()

# Include all routers (NO AUTH ROUTER)
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(download_router, prefix="/download", tags=["download"])
api_router.include_router(employee_router, prefix="/employee", tags=["employee"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(status_router, prefix="/status", tags=["status"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(websocket_router, prefix="/ws", tags=["websocket"])