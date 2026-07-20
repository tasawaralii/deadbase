from fastapi import APIRouter

from app.api.routes.author import (
    animes,
    comments,
    episodes,
    images,
    links,
    packs,
    posts,
    season_dubs,
    seasons,
    stream_comments,
    tmdb,
)

# Content-management API - authors (scoped by access_scope) and superusers.
# Not superuser-only; see app/api/routes/admin for that.
router = APIRouter(prefix="/author", tags=["author"])
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
router.include_router(posts.router)
router.include_router(season_dubs.router)
