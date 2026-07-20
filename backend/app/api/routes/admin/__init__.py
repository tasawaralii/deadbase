from fastapi import APIRouter

from app.api.routes.admin import servers, shorteners, stats, unlock_config, users

# Superuser-only config. Content CRUD lives under /author instead (see
# app.api.routes.author) - accessible to authors, not superuser-only,
# despite historically having lived here too.
router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(users.router)
router.include_router(shorteners.router)
router.include_router(servers.router)
router.include_router(unlock_config.router)
router.include_router(stats.router)
