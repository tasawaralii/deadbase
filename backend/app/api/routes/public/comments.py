from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from sqlmodel import col, select

from app.api.deps import SessionDep
from app.comments import initial_status, is_blocked_email, is_rejected_body
from app.content import get_playable_content
from app.models import CommentStatus, StreamComments
from app.schemas.common import CommentCreate, CommentPublic

router = APIRouter()


def _comment_public(comment: StreamComments) -> CommentPublic:
    return CommentPublic(
        id=comment.id,
        parent_id=comment.parent_id,
        author_name=comment.author_name,
        author_url=comment.author_url,
        body=comment.body,
        created_at=comment.created_at,
    )


@router.get("/content/{content_id}/comments")
def list_content_comments(
    session: SessionDep, content_id: int
) -> list[CommentPublic]:
    if not get_playable_content(session, content_id):
        raise HTTPException(status_code=404, detail="Content not found")

    comments = session.exec(
        select(StreamComments)
        .where(
            StreamComments.content_id == content_id,
            StreamComments.status == CommentStatus.APPROVED,
        )
        .order_by(col(StreamComments.created_at).asc())
    ).all()
    return [_comment_public(c) for c in comments]


@router.post("/content/{content_id}/comments", status_code=201)
def create_content_comment(
    session: SessionDep, content_id: int, comment_in: CommentCreate
) -> CommentPublic:
    if not get_playable_content(session, content_id):
        raise HTTPException(status_code=404, detail="Content not found")

    if comment_in.parent_id is not None:
        parent = session.exec(
            select(StreamComments).where(
                StreamComments.id == comment_in.parent_id,
                StreamComments.content_id == content_id,
            )
        ).first()
        if not parent:
            raise HTTPException(
                status_code=400, detail="parent_id does not belong to this content"
            )

    if is_blocked_email(comment_in.author_email):
        raise HTTPException(status_code=400, detail="Comment rejected")

    if is_rejected_body(comment_in.body):
        raise HTTPException(status_code=400, detail="Comment rejected")

    duplicate = session.exec(
        select(StreamComments).where(
            StreamComments.content_id == content_id,
            StreamComments.author_name == comment_in.author_name,
            StreamComments.author_email == comment_in.author_email,
            StreamComments.body == comment_in.body,
        )
    ).first()
    if duplicate:
        return _comment_public(duplicate)

    comment = StreamComments(
        content_id=content_id,
        parent_id=comment_in.parent_id,
        author_name=comment_in.author_name,
        author_email=comment_in.author_email,
        author_url=comment_in.author_url,
        body=comment_in.body,
        created_at=datetime.now(UTC),
        status=initial_status(comment_in.body),
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _comment_public(comment)
