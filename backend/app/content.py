from sqlmodel import Session

from app.models import Content, ContentContentType, Episodes, Packs, Seasons

PLAYABLE_TYPES = (ContentContentType.MOVIE, ContentContentType.EPISODE)


def get_playable_content(session: Session, content_id: int) -> Content | None:
    """Movies and episode1s have a player page; packs don't."""
    content = session.get(Content, content_id)
    if not content or content.content_type not in PLAYABLE_TYPES:
        return None
    return content


def resolve_anime_id_for_content(session: Session, content: Content) -> int | None:
    """
    Traces a Content row back to the anime it ultimately belongs to, for
    permission checks (see app.permissions.require_anime_write_access).
    Movies point at their anime directly; episodes/packs need one more hop
    through their season.
    """
    if content.respective_id is None:
        return None

    if content.content_type == ContentContentType.MOVIE:
        return content.respective_id

    if content.content_type == ContentContentType.EPISODE:
        episode = session.get(Episodes, content.respective_id)
        if episode is None:
            return None
        season = session.get(Seasons, episode.season_id)
        return season.anime_id if season else None

    if content.content_type == ContentContentType.PACK:
        pack = session.get(Packs, content.respective_id)
        if pack is None:
            return None
        season = session.get(Seasons, pack.season_id)
        return season.anime_id if season else None

    return None
