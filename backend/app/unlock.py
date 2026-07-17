import secrets
import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

import httpx
from sqlmodel import Session, col, func, select

from app.models import DownloadEvents, LinkShorteners, ShortenerAttempts, UnlockConfig

REPORT_WINDOW = timedelta(hours=24)

TOKEN_VALIDITY = timedelta(minutes=30)
SOLVE_WINDOW = timedelta(hours=24)


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def get_unlock_config(session: Session) -> UnlockConfig:
    config = session.get(UnlockConfig, 1)
    if not config:
        config = UnlockConfig(id=1, required_solves=4)
        session.add(config)
        session.commit()
        session.refresh(config)
    return config


def solved_shortener_ids(session: Session, visitor_id: uuid.UUID) -> set[int]:
    cutoff = datetime.now(UTC) - SOLVE_WINDOW
    rows = session.exec(
        select(ShortenerAttempts.shortener_id).where(
            ShortenerAttempts.visitor_id == visitor_id,
            col(ShortenerAttempts.solved_at).is_not(None),
            col(ShortenerAttempts.solved_at) > cutoff,
        )
    ).all()
    return set(rows)


def is_unlocked(session: Session, visitor_id: uuid.UUID) -> bool:
    config = get_unlock_config(session)
    return len(solved_shortener_ids(session, visitor_id)) >= config.required_solves


def reported_shortener_ids(session: Session, visitor_id: uuid.UUID) -> set[int]:
    cutoff = datetime.now(UTC) - SOLVE_WINDOW
    rows = session.exec(
        select(ShortenerAttempts.shortener_id).where(
            ShortenerAttempts.visitor_id == visitor_id,
            col(ShortenerAttempts.reported_at).is_not(None),
            col(ShortenerAttempts.reported_at) > cutoff,
        )
    ).all()
    return set(rows)


def maybe_auto_disable(session: Session, shortener_id: int) -> None:
    """
    If enough distinct visitors have reported this shortener recently, disable
    it automatically rather than waiting for an admin to notice - a broken
    shortener actively hurts the unlock flow for everyone in the meantime.
    Counts distinct visitors, not raw reports, so one visitor spamming reports
    can't get a shortener disabled on their own.
    """
    config = get_unlock_config(session)
    cutoff = datetime.now(UTC) - REPORT_WINDOW
    reporter_count = session.exec(
        select(func.count(func.distinct(ShortenerAttempts.visitor_id))).where(
            ShortenerAttempts.shortener_id == shortener_id,
            col(ShortenerAttempts.reported_at).is_not(None),
            col(ShortenerAttempts.reported_at) > cutoff,
        )
    ).one()
    if reporter_count >= config.report_threshold:
        shortener = session.get(LinkShorteners, shortener_id)
        if shortener and shortener.is_enabled:
            shortener.is_enabled = False
            session.add(shortener)
            session.commit()


def resolve_shortener_url(shortener: LinkShorteners, target_url: str) -> str:
    encoded = quote(target_url, safe="")
    api_url = shortener.api_url_template + encoded
    try:
        resp = httpx.get(api_url, timeout=5.0)
        data = resp.json()
        if data.get("status") == "success" and data.get("shortenedUrl"):
            return str(data["shortenedUrl"])
    except (httpx.HTTPError, ValueError, KeyError):
        pass
    return shortener.quick_url_template + encoded


def record_download_event(
    session: Session,
    visitor_id: uuid.UUID,
    link_server_id: int,
    via_shortener_id: int | None,
) -> None:
    session.add(
        DownloadEvents(
            link_server_id=link_server_id,
            visitor_id=visitor_id,
            via_shortener_id=via_shortener_id,
        )
    )
    session.commit()
