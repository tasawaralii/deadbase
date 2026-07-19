from fastapi import APIRouter

from app.api.routes.admin import comments, images, stream_comments, tmdb

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(comments.router)
router.include_router(stream_comments.router)
router.include_router(images.router)
router.include_router(tmdb.router)
