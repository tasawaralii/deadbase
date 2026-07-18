from fastapi import APIRouter

from app.api.routes.admin import comments, stream_comments

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(comments.router)
router.include_router(stream_comments.router)
