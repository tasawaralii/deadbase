import datetime as dt

from sqlmodel import SQLModel

from app.models import CommentStatus
from app.schemas.common import ImageUrls


class AdminImageUploadPublic(SQLModel):
    image: str
    urls: ImageUrls


class AdminCommentPublic(SQLModel):
    id: int
    post_id: int
    post_slug: str
    post_title: str
    parent_id: int | None
    author_name: str
    author_email: str
    author_url: str | None
    body: str
    created_at: dt.datetime
    status: CommentStatus


class AdminCommentListPublic(SQLModel):
    data: list[AdminCommentPublic]
    count: int


class AdminStreamCommentPublic(SQLModel):
    id: int
    content_id: int
    parent_id: int | None
    author_name: str
    author_email: str
    author_url: str | None
    body: str
    created_at: dt.datetime
    status: CommentStatus


class AdminStreamCommentListPublic(SQLModel):
    data: list[AdminStreamCommentPublic]
    count: int


class AdminCommentStatusUpdate(SQLModel):
    status: CommentStatus
