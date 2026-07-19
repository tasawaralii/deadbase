import datetime as dt
from typing import Literal

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

# New content only ever gets created with a tmdb-sourced or freshly-uploaded
# bucket image - "url" and legacy "local" are read-only holdovers from the
# old PHP migration, never offered for new rows.
NewImageSource = Literal["tmdb", "bucket"]


class CommentPublic(SQLModel):
    id: int
    parent_id: int | None
    author_name: str
    author_url: str | None
    avatar_url: str
    body: str
    created_at: dt.datetime


class CommentCreate(SQLModel):
    author_name: str = Field(min_length=1, max_length=50)
    author_email: EmailStr
    author_url: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=1, max_length=2000)
    parent_id: int | None = None


class CommentListPublic(SQLModel):
    data: list[CommentPublic]
    page: int
    limit: int
    # Comments are paginated by root (top-level) thread, not by raw row count,
    # so a reply never gets split onto a different page than its parent -
    # `data` for one page can contain more than `limit` rows once replies are
    # included. root_count drives "is there another page"; total_count is the
    # full comment+reply tally for the "N Comments" header.
    root_count: int
    total_count: int


class ImageUrls(SQLModel):
    low: str
    mid: str
    high: str


class DownloadLink(SQLModel):
    name: str
    link_server_id: int
    color: str


class LinkPublic(SQLModel):
    quality: str
    size: str
    servers: list[DownloadLink]
    only_hindi: bool
    note: str


class SeasonDub(SQLModel):
    platform: str
    language: str


class AuthorPublic(SQLModel):
    display_name: str
    slug: str
    avatar_url: str


class TagPublic(SQLModel):
    name: str
    slug: str


class GenrePublic(SQLModel):
    name: str
    slug: str
