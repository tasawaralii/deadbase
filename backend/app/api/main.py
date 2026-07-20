from fastapi import APIRouter

from app.api.routes import admin, author, login, me, private, public, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(me.router)
api_router.include_router(utils.router)
api_router.include_router(public.router)
api_router.include_router(admin.router)
api_router.include_router(author.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
