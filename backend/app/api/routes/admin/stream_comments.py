from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import and_, col, func, or_, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.content import resolve_anime_id_for_content, resolve_season_for_content
from app.models import (
    AuthorAccessScope,
    AuthorAnimeAccess,
    CommentStatus,
    Content,
    ContentContentType,
    Episodes,
    Seasons,
    SeasonStatus,
    StreamComments,
)
from app.permissions import require_anime_write_access
from app.schemas.admin import (
    AdminCommentStatusUpdate,
    AdminStreamCommentListPublic,
    AdminStreamCommentPublic,
)

router = APIRouter(
    prefix="/stream-comments",
    tags=["admin"],
    dependencies=[Depends(get_current_author)],
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


def _get_stream_comment_with_access(
    session: SessionDep, author: CurrentAuthor, comment_id: int
) -> StreamComments:
    comment = session.get(StreamComments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    content = session.get(Content, comment.content_id)
    anime_id = resolve_anime_id_for_content(session, content) if content else None
    if anime_id is None:
        raise HTTPException(status_code=404, detail="Comment has no resolvable owner")
    season = resolve_season_for_content(session, content) if content else None
    require_anime_write_access(session, author, anime_id, season=season)

    return comment


@router.get("/")
def list_stream_comments(
    session: SessionDep,
    author: CurrentAuthor,
    status: Annotated[CommentStatus | None, Query()] = None,
    skip: int = 0,
    limit: int = 50,
) -> AdminStreamCommentListPublic:
    filters = [StreamComments.status == status] if status else []

    query = select(StreamComments).join(
        Content, col(StreamComments.content_id) == col(Content.id)
    )

    # Same scoping as comments.py, just walking content_id -> Content ->
    # (movie: respective_id is the anime_id directly) or (episode: one hop
    # through Episodes -> Seasons). Packs never get stream comments.
    if not author.is_superuser and author.access_scope in (
        AuthorAccessScope.ACCESS_LIST,
        AuthorAccessScope.ONGOING,
    ):
        query = query.outerjoin(
            Episodes, col(Content.id) == col(Episodes.content_id)
        ).outerjoin(Seasons, col(Episodes.season_id) == col(Seasons.season_id))

        if author.access_scope == AuthorAccessScope.ACCESS_LIST:
            granted_anime_ids = select(AuthorAnimeAccess.anime_id).where(
                AuthorAnimeAccess.user_id == author.id
            )
            query = query.where(
                or_(
                    and_(
                        Content.content_type == ContentContentType.MOVIE,
                        col(Content.respective_id).in_(granted_anime_ids),
                    ),
                    col(Seasons.anime_id).in_(granted_anime_ids),
                )
            )
        else:
            query = query.where(
                or_(
                    Content.content_type == ContentContentType.MOVIE,
                    Seasons.status == SeasonStatus.ONGOING,
                )
            )

    query = query.where(*filters)

    count = session.exec(
        select(func.count()).select_from(
            query.with_only_columns(col(StreamComments.id)).subquery()
        )
    ).one()

    rows = session.exec(
        query.order_by(col(StreamComments.created_at).desc()).offset(skip).limit(limit)
    ).all()

    return AdminStreamCommentListPublic(
        data=[_admin_stream_comment_public(c) for c in rows], count=count
    )


@router.patch("/{comment_id}")
def update_stream_comment_status(
    session: SessionDep, author: CurrentAuthor, comment_id: int, body: AdminCommentStatusUpdate
) -> AdminStreamCommentPublic:
    comment = _get_stream_comment_with_access(session, author, comment_id)

    comment.status = body.status
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _admin_stream_comment_public(comment)


@router.delete("/{comment_id}", status_code=204)
def delete_stream_comment(session: SessionDep, author: CurrentAuthor, comment_id: int) -> None:
    comment = _get_stream_comment_with_access(session, author, comment_id)
    session.delete(comment)
    session.commit()
