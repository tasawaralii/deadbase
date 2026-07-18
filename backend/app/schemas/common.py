import datetime as dt

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


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
