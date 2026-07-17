from fastapi import APIRouter

from app.api.routes.public import anime, episode, pack, post, season, unlock

router = APIRouter(prefix="/public", tags=["public"])
router.include_router(anime.router)
router.include_router(season.router)
router.include_router(episode.router)
router.include_router(pack.router)
router.include_router(post.router)
router.include_router(unlock.router)
