import datetime as dt

from sqlmodel import SQLModel

from app.models import PostStatus
from app.schemas.common import TagPublic


class PostUpdate(SQLModel):
    # slug is deliberately not editable here - it's a public URL, changing
    # it breaks existing links/bookmarks/SEO. Everything else about a post
    # is fair game.
    title: str | None = None
    backdrop_img: str | None = None
    status: PostStatus | None = None
    sticky: bool | None = None
    tag_ids: list[int] | None = None


class PostAdminPublic(SQLModel):
    id: int
    anime_id: int | None
    season_id: int | None
    title: str
    slug: str
    backdrop_img: str | None
    status: PostStatus
    sticky: bool
    views: int
    last_updated: dt.datetime
    tags: list[TagPublic]
