import decimal
from typing import Literal

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Links, LinkServers
from app.schemas.common import DownloadLink, ImageUrls, LinkPublic

TMDB_IMAGE_DOMAIN = "https://image.tmdb.org/t/p/"

_TMDB_SIZES: dict[str, dict[str, str]] = {
    "poster": {"low": "w154", "mid": "w342", "high": "w780"},
    "backdrop": {"low": "w300", "mid": "w780", "high": "w1280"},
}

_SIZE_UNITS = ("B", "KB", "MB", "GB", "TB")

_SERVER_LINK_PATTERNS: dict[str, str] = {
    "filepress": "https://{domain}/file/{slug}",
    "hubcloud": "https://{domain}/drive/{slug}",
    "neodrive": "https://{domain}/file/{slug}",
    "gdflix": "https://{domain}/file/{slug}",
    "pixeldrain": "https://pixeldrain.com/u/{slug}",
    "telegram": "https://t.me/{domain}?start={slug}",
}


def resolve_image_urls(
    source: str, image: str | None, kind: Literal["poster", "backdrop"]
) -> ImageUrls:
    """
    tmdb: build low/mid/high variants from the tmdb path.
    local ("own"): single resolution, prefixed with MEDIA_BASE_URL.
    url: legacy full external URL, passed through until migrated to "own".
    """
    if not image:
        return ImageUrls(low="", mid="", high="")

    if source == "tmdb":
        sizes = _TMDB_SIZES[kind]
        return ImageUrls(
            low=f"{TMDB_IMAGE_DOMAIN}{sizes['low']}{image}",
            mid=f"{TMDB_IMAGE_DOMAIN}{sizes['mid']}{image}",
            high=f"{TMDB_IMAGE_DOMAIN}{sizes['high']}{image}",
        )

    if source == "local":
        url = f"{settings.MEDIA_BASE_URL}{image}"
        return ImageUrls(low=url, mid=url, high=url)

    return ImageUrls(low=image, mid=image, high=image)


def resolve_server_link(server_sid: str, domain: str, slug: str) -> str | None:
    pattern = _SERVER_LINK_PATTERNS.get(server_sid)
    if not pattern:
        return None
    return pattern.format(domain=domain, slug=slug)


def format_size(size: decimal.Decimal | None) -> str:
    value = float(size) if size is not None else 0.0
    unit_index = 0
    while value >= 1024 and unit_index < len(_SIZE_UNITS) - 1:
        value /= 1024
        unit_index += 1
    return f"{round(value, 2)} {_SIZE_UNITS[unit_index]}"


def build_download_links(session: Session, content_id: int) -> list[LinkPublic]:
    links = session.exec(
        select(Links)
        .where(Links.content_id == content_id, Links.is_live == True)  # noqa: E712
        .options(
            selectinload(Links.quality),  # type: ignore[arg-type]
            selectinload(Links.link_servers).selectinload(  # type: ignore[arg-type]
                LinkServers.server  # type: ignore[arg-type]
            ),
        )
    ).all()

    result = []
    for link in links:
        servers = []
        for ls in link.link_servers:
            if not ls.slug or not ls.server.is_enabled:
                continue
            # Only used to validate this server config can actually resolve to
            # something; the real URL is never exposed here (see app/unlock.py) -
            # it's only ever resolved server-side once a visitor is unlocked.
            href = resolve_server_link(ls.server.server_sid, ls.server.server_domain, ls.slug)
            if not href:
                continue
            servers.append(
                DownloadLink(
                    name=ls.server.server_name,
                    link_server_id=ls.ser_link_id,
                    color=ls.server.color,
                )
            )
        result.append(
            LinkPublic(
                quality=link.quality.quality_name if link.quality else "Unknown",
                size=format_size(link.size),
                servers=servers,
                only_hindi=link.only_hindi,
                note=link.note,
            )
        )
    return result


def get_watch_servers() -> list[DownloadLink]:
    """
    No streaming sources wired up yet (see MEDIA_BASE_URL / future streaming
    site plan). Returns an empty list so the frontend can hide the "watch
    online" action; populate this once a source exists, same shape either way.
    """
    return []
