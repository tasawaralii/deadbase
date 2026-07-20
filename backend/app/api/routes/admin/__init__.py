from fastapi import APIRouter

from app.api.routes.admin import users

# Superuser-only config: user/author account administration today, and the
# future home for shortener/server/stats config. Content CRUD lives under
# /author instead (see app.api.routes.author) - accessible to authors, not
# superuser-only, despite historically having lived here too.
router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(users.router)
