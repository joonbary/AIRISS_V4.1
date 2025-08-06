"""
API v1 Router
모든 v1 엔드포인트 통합
"""

from fastapi import APIRouter

# Import all routers
from .endpoints.auth import router as auth_router
from .endpoints.analysis import router as analysis_router
from .endpoints.files import router as files_router
from .endpoints.users import router as users_router
from .endpoints.websocket import router as ws_router
from .endpoints.workflow import router as workflow_router
from .endpoints.employees import router as employees_router
from .endpoints.openai_proxy import router as openai_proxy_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])
api_router.include_router(employees_router, prefix="/employees", tags=["Employees"])
api_router.include_router(openai_proxy_router, prefix="/proxy/openai", tags=["OpenAI Proxy"])

__all__ = ["api_router"]