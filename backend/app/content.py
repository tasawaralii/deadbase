from sqlmodel import Session

from app.models import Content, ContentContentType

PLAYABLE_TYPES = (ContentContentType.MOVIE, ContentContentType.EPISODE)


def get_playable_content(session: Session, content_id: int) -> Content | None:
    """Movies and episodes have a player page; packs don't."""
    content = session.get(Content, content_id)
    if not content or content.content_type not in PLAYABLE_TYPES:
        return None
    return content
