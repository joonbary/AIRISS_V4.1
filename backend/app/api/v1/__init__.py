"""
API v1 Router
모든 v1 엔드포인트 통합
"""

from fastapi import APIRouter

# Import all routers
from .auth import router as auth_router
from .analysis import router as analysis_router
from .files import router as files_router
from .users import router as users_router
from .websocket import router as ws_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

__all__ = ["api_router"]