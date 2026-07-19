from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import AuthorAccessScope, AuthorAnimeAccess, Seasons, SeasonStatus, User


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


def require_anime_write_access(
    session: Session, author: User, anime_id: int, season: Seasons | None = None
) -> None:
    """
    Gates writes to an existing anime (adding a season, episode, link, etc).

    all authors can touch any anime, unrestricted. ongoing authors can touch
    any anime too, but only the specific season being written to (if any) -
    pass the Season being acted on (via `season`) whenever the operation is
    scoped to one (episode/pack/link writes); leave it unset for anime- or
    season-creation-level operations where there's no existing season to
    check, or for movie content (which has no season at all) - a newly
    created season starts out `ongoing` by definition, so there's nothing to
    restrict at creation time. access_list authors are limited to anime
    explicitly granted via AuthorAnimeAccess, with no season restriction -
    a grant covers every season of that anime, ongoing or not.
    """
    if author.is_superuser or author.access_scope == AuthorAccessScope.ALL:
        return

    if author.access_scope == AuthorAccessScope.ONGOING:
        if season is not None and season.status != SeasonStatus.ONGOING:
            raise HTTPException(
                status_code=403,
                detail="This season has been marked completed - only ongoing seasons are editable on your account",
            )
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
