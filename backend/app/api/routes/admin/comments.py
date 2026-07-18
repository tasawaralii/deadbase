from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Comments, CommentStatus, Posts
from app.schemas.admin import (
    AdminCommentListPublic,
    AdminCommentPublic,
    AdminCommentStatusUpdate,
)

router = APIRouter(
    prefix="/comments",
    tags=["admin"],
    dependencies=[Depends(get_current_active_superuser)],
)


def _admin_comment_public(comment: Comments, post: Posts) -> AdminCommentPublic:
    return AdminCommentPublic(
        id=comment.id,
        post_id=post.id,
        post_slug=post.slug,
        post_title=post.title,
        parent_id=comment.parent_id,
        author_name=comment.author_name,
        author_email=comment.author_email,
        author_url=comment.author_url,
        body=comment.body,
        created_at=comment.created_at,
        status=comment.status,
    )


@router.get("/")
def list_comments(
    session: SessionDep,
    status: Annotated[CommentStatus | None, Query()] = None,
    skip: int = 0,
    limit: int = 50,
) -> AdminCommentListPublic:
    filters = [Comments.status == status] if status else []

    count = session.exec(
        select(func.count()).select_from(Comments).where(*filters)
    ).one()

    rows = session.exec(
        select(Comments, Posts)
        .join(Posts, col(Comments.post_id) == col(Posts.id))
        .where(*filters)
        .order_by(col(Comments.created_at).desc())
        .offset(skip)
        .limit(limit)
    ).all()

    return AdminCommentListPublic(
        data=[_admin_comment_public(comment, post) for comment, post in rows],
        count=count,
    )


@router.patch("/{comment_id}")
def update_comment_status(
    session: SessionDep, comment_id: int, body: AdminCommentStatusUpdate
) -> AdminCommentPublic:
    comment = session.get(Comments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.status = body.status
    session.add(comment)
    session.commit()
    session.refresh(comment)

    post = session.get(Posts, comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _admin_comment_public(comment, post)


@router.delete("/{comment_id}", status_code=204)
def delete_comment(session: SessionDep, comment_id: int) -> None:
    comment = session.get(Comments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    session.delete(comment)
    session.commit()
