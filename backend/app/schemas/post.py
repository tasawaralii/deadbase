import datetime as dt

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models import PostStatus
from app.schemas.anime import AnimeDetail
from app.schemas.season import SeasonDetail


class CommentPublic(SQLModel):
    id: int
    parent_id: int | None
    author_name: str
    author_url: str | None
    body: str
    created_at: dt.datetime


class CommentCreate(SQLModel):
    author_name: str = Field(min_length=1, max_length=50)
    author_email: EmailStr
    author_url: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=1, max_length=2000)
    parent_id: int | None = None


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
