from fastapi import APIRouter
from .analyze import router as analyze_router
from .preview import router as preview_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all routers
api_router.include_router(analyze_router)
api_router.include_router(preview_router) 