"""
API v1 router - combines all v1 API routers.
"""
from fastapi import APIRouter
from src.api.v1.tasks import router as tasks_router
from src.api.v1.auth import router as auth_router

# Create main API v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(tasks_router)
