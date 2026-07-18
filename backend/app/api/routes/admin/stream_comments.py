from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import CommentStatus, StreamComments
from app.schemas.admin import (
    AdminCommentStatusUpdate,
    AdminStreamCommentListPublic,
    AdminStreamCommentPublic,
)

router = APIRouter(
    prefix="/stream-comments",
    tags=["admin"],
    dependencies=[Depends(get_current_active_superuser)],
)


def _admin_stream_comment_public(
    comment: StreamComments,
) -> AdminStreamCommentPublic:
    return AdminStreamCommentPublic(
        id=comment.id,
        content_id=comment.content_id,
        parent_id=comment.parent_id,
        author_name=comment.author_name,
        author_email=comment.author_email,
        author_url=comment.author_url,
        body=comment.body,
        created_at=comment.created_at,
        status=comment.status,
    )


@router.get("/")
def list_stream_comments(
    session: SessionDep,
    status: Annotated[CommentStatus | None, Query()] = None,
    skip: int = 0,
    limit: int = 50,
) -> AdminStreamCommentListPublic:
    filters = [StreamComments.status == status] if status else []

    count = session.exec(
        select(func.count()).select_from(StreamComments).where(*filters)
    ).one()

    rows = session.exec(
        select(StreamComments)
        .where(*filters)
        .order_by(col(StreamComments.created_at).desc())
        .offset(skip)
        .limit(limit)
    ).all()

    return AdminStreamCommentListPublic(
        data=[_admin_stream_comment_public(c) for c in rows], count=count
    )


@router.patch("/{comment_id}")
def update_stream_comment_status(
    session: SessionDep, comment_id: int, body: AdminCommentStatusUpdate
) -> AdminStreamCommentPublic:
    comment = session.get(StreamComments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.status = body.status
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _admin_stream_comment_public(comment)


@router.delete("/{comment_id}", status_code=204)
def delete_stream_comment(session: SessionDep, comment_id: int) -> None:
    comment = session.get(StreamComments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    session.delete(comment)
    session.commit()
