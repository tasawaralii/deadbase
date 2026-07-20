from fastapi import APIRouter

from app.api.routes.admin import (
    age_ratings,
    genres,
    languages,
    ott_platforms,
    qualities,
    servers,
    shorteners,
    stats,
    tags,
    unlock_config,
    upload_queue,
    users,
)

# Superuser-only config. Content CRUD lives under /author instead (see
# app.api.routes.author) - accessible to authors, not superuser-only,
# despite historically having lived here too.
router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(users.router)
router.include_router(shorteners.router)
router.include_router(servers.router)
router.include_router(unlock_config.router)
router.include_router(stats.router)
router.include_router(upload_queue.router)
router.include_router(age_ratings.router)
router.include_router(genres.router)
router.include_router(qualities.router)
router.include_router(languages.router)
router.include_router(ott_platforms.router)
router.include_router(tags.router)
