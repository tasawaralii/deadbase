from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import AuthorAccessScope, AuthorAnimeAccess, User


def require_can_create_anime(author: User) -> None:
    """
    Net-new anime creation is out of scope for access_list authors - that
    tier only manages anime already assigned to it, and a brand-new anime
    can't be on anyone's list yet.
    """
    if not author.is_superuser and author.access_scope == AuthorAccessScope.ACCESS_LIST:
        raise HTTPException(
            status_code=403,
            detail="Your account can only manage anime already assigned to it",
        )


def require_anime_write_access(session: Session, author: User, anime_id: int) -> None:
    """
    Gates writes to an existing anime (adding a season, episode, link, etc).
    all/ongoing authors can touch any anime - anything newly added under it
    starts out ongoing by definition, so there's nothing to restrict at
    creation time. access_list authors are limited to anime explicitly
    granted via AuthorAnimeAccess.
    """
    if author.is_superuser or author.access_scope in (
        AuthorAccessScope.ALL,
        AuthorAccessScope.ONGOING,
    ):
        return

    if author.access_scope == AuthorAccessScope.ACCESS_LIST:
        granted = session.exec(
            select(AuthorAnimeAccess).where(
                AuthorAnimeAccess.user_id == author.id,
                AuthorAnimeAccess.anime_id == anime_id,
            )
        ).first()
        if granted is not None:
            return

    raise HTTPException(
        status_code=403, detail="You don't have access to manage this anime"
    )
