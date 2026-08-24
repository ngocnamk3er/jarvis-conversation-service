from fastapi import APIRouter
from app.api.v1.endpoints import health, conversations

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
