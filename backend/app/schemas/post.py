import datetime as dt

from sqlmodel import SQLModel

from app.models import PostStatus
from app.schemas.anime import AnimeDetail
from app.schemas.common import (
    AuthorPublic,
    CommentCreate,
    CommentListPublic,
    CommentPublic,
    ImageUrls,
    TagPublic,
)
from app.schemas.season import SeasonDetail

__all__ = [
    "CommentCreate",
    "CommentListPublic",
    "CommentPublic",
    "PostDetail",
    "PostListPublic",
    "PostSummary",
    "TagPublic",
]


class PostSummary(SQLModel):
    slug: str
    title: str
    backdrop_img: ImageUrls
    status: PostStatus
    sticky: bool
    views: int
    last_updated: dt.datetime
    tags: list[TagPublic]
    comment_count: int
    author: AuthorPublic | None
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
    backdrop_img: ImageUrls
    status: PostStatus
    sticky: bool
    views: int
    last_updated: dt.datetime
    tags: list[TagPublic]
    author: AuthorPublic | None
    anime_slug: str
    anime_name: str
    genres: list[str]
    anime: AnimeDetail | None
    season: SeasonDetail | None
