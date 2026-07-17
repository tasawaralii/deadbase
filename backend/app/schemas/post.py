import datetime as dt

from sqlmodel import SQLModel

from app.models import PostStatus
from app.schemas.anime import AnimeDetail
from app.schemas.common import CommentCreate, CommentPublic
from app.schemas.season import SeasonDetail

__all__ = ["CommentCreate", "CommentPublic", "PostDetail", "PostListPublic", "PostSummary"]


class PostSummary(SQLModel):
    slug: str
    title: str
    backdrop_img: str | None
    status: PostStatus
    sticky: bool
    views: int
    last_updated: dt.datetime
    tags: list[str]
    comment_count: int
    anime_slug: str
    anime_name: str
    season_number: int | None
    type: str


class PostListPublic(SQLModel):
    data: list[PostSummary]
    page: int
    limit: int
    count: int


class PostDetail(SQLModel):
    slug: str
    title: str
    backdrop_img: str | None
    status: PostStatus
    sticky: bool
    views: int
    last_updated: dt.datetime
    tags: list[str]
    anime_slug: str
    anime_name: str
    genres: list[str]
    anime: AnimeDetail | None
    season: SeasonDetail | None
    comments: list[CommentPublic]
