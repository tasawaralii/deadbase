from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, or_, select

from app.api.deps import CurrentAuthor, SessionDep, get_current_author
from app.models import (
    AuthorAccessScope,
    AuthorAnimeAccess,
    Comments,
    CommentStatus,
    Posts,
    Seasons,
    SeasonStatus,
)
from app.permissions import require_anime_write_access
from app.schemas.admin import (
    AdminCommentListPublic,
    AdminCommentPublic,
    AdminCommentStatusUpdate,
)

router = APIRouter(
    prefix="/comments",
    tags=["author"],
    dependencies=[Depends(get_current_author)],
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


def _get_comment_with_access(
    session: SessionDep, author: CurrentAuthor, comment_id: int
) -> tuple[Comments, Posts]:
    comment = session.get(Comments, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    post = session.get(Posts, comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.anime_id is not None:
        require_anime_write_access(session, author, post.anime_id)
    else:
        season = session.get(Seasons, post.season_id)
        if season is None:
            raise HTTPException(status_code=404, detail="Season not found")
        require_anime_write_access(session, author, season.anime_id, season=season)

    return comment, post


@router.get("/")
def list_comments(
    session: SessionDep,
    author: CurrentAuthor,
    status: Annotated[CommentStatus | None, Query()] = None,
    skip: int = 0,
    limit: int = 50,
) -> AdminCommentListPublic:
    filters = [Comments.status == status] if status else []

    query = select(Comments, Posts).join(Posts, col(Comments.post_id) == col(Posts.id))

    # Comment moderation is scoped the same way as everything else under an
    # anime - access_list authors only see comments on anime/seasons granted
    # to them, ongoing authors only see comments on movies (unrestricted,
    # no season) or seasons currently flagged ongoing. superuser/all see
    # everything.
    if not author.is_superuser and author.access_scope == AuthorAccessScope.ACCESS_LIST:
        granted_anime_ids = select(AuthorAnimeAccess.anime_id).where(
            AuthorAnimeAccess.user_id == author.id
        )
        query = query.outerjoin(Seasons, col(Posts.season_id) == col(Seasons.season_id)).where(
            or_(
                col(Posts.anime_id).in_(granted_anime_ids),
                col(Seasons.anime_id).in_(granted_anime_ids),
            )
        )
    elif not author.is_superuser and author.access_scope == AuthorAccessScope.ONGOING:
        query = query.outerjoin(Seasons, col(Posts.season_id) == col(Seasons.season_id)).where(
            or_(
                col(Posts.anime_id).isnot(None),
                Seasons.status == SeasonStatus.ONGOING,
            )
        )

    query = query.where(*filters)

    count = session.exec(
        select(func.count()).select_from(query.with_only_columns(col(Comments.id)).subquery())
    ).one()

    rows = session.exec(
        query.order_by(col(Comments.created_at).desc()).offset(skip).limit(limit)
    ).all()

    return AdminCommentListPublic(
        data=[_admin_comment_public(comment, post) for comment, post in rows],
        count=count,
    )


@router.patch("/{comment_id}")
def update_comment_status(
    session: SessionDep, author: CurrentAuthor, comment_id: int, body: AdminCommentStatusUpdate
) -> AdminCommentPublic:
    comment, post = _get_comment_with_access(session, author, comment_id)

    comment.status = body.status
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _admin_comment_public(comment, post)


@router.delete("/{comment_id}", status_code=204)
def delete_comment(session: SessionDep, author: CurrentAuthor, comment_id: int) -> None:
    comment, _ = _get_comment_with_access(session, author, comment_id)
    session.delete(comment)
    session.commit()
