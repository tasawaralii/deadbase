from fastapi import APIRouter

from app.api.routes.admin import (
    animes,
    comments,
    episodes,
    images,
    links,
    packs,
    seasons,
    stream_comments,
    tmdb,
)

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(comments.router)
router.include_router(stream_comments.router)
router.include_router(images.router)
router.include_router(tmdb.router)
router.include_router(animes.router)
router.include_router(seasons.router)
router.include_router(seasons.season_router)
router.include_router(episodes.router)
router.include_router(packs.router)
router.include_router(links.router)
router.include_router(links.single_link_router)
router.include_router(links.season_links_router)
router.include_router(links.gdrive_router)
