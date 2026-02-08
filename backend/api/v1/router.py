from fastapi import APIRouter

from backend.api.v1.health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
